"""Bake a local review candidate from the preserved approved v5.8 checkpoint.

Run in background Blender. Only arm-chain rotations in SwordAttack, Victory
and TownIdle change. Hands retain their original local rotations and grips.
No runtime IK, new rig, mesh change, or Studio pose-key override is introduced.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Quaternion, Vector

PACKAGE = Path(__file__).resolve().parents[1]
BASELINE = PACKAGE / 'Blender/arin-v5.8-approved-before-motion-repair.blend'
OUTPUT = PACKAGE / 'Blender/arin-v5.8-all-animations.blend'
REPAIRED = ('SwordAttack', 'Victory', 'TownIdle')


def envelope(frame, keys):
    for (start, value), (end, next_value) in zip(keys, keys[1:]):
        if start <= frame <= end:
            t = (frame - start) / (end - start)
            return value + (next_value - value) * t * t * (3 - 2 * t)
    return 0.0


def target_offset(clip, frame, side):
    if clip == 'SwordAttack':
        if side == 'Right':
            weight = envelope(frame, [(1, 0), (19, 0), (25, 1), (36, 1), (43, 0), (46, 0)])
            return Vector((0, -.14, .07)) * weight
        weight = envelope(frame, [(1, 0), (26, 0), (31, 1), (36, 1), (42, 0), (46, 0)])
        return Vector((.08, -.015, .065)) * weight
    if clip == 'Victory':
        return Vector((-.055 if side == 'Right' else .065, -.025, .025))
    if clip == 'TownIdle' and side == 'Right':
        weight = envelope(frame, [(1, 0), (10, 0), (19, 1), (43, 1), (52, 0), (61, 0)])
        return Vector((-.025, -.01, .003)) * weight
    return Vector((0, 0, 0))


def arm_state(rig, side):
    upper, lower, hand = [rig.pose.bones['mixamorig:' + side + part]
                          for part in ('Arm', 'ForeArm', 'Hand')]
    return {'shoulder': upper.head.copy(), 'elbow': lower.head.copy(),
            'wrist': hand.head.copy(), 'upper': upper.matrix.copy(),
            'lower': lower.matrix.copy()}


def set_rotation(bone, rotation):
    parent = bone.parent.matrix @ bone.parent.bone.matrix_local.inverted() @ bone.bone.matrix_local
    quaternion = parent.to_quaternion().inverted() @ rotation
    if quaternion.dot(bone.rotation_quaternion) < 0:
        quaternion.negate()
    bone.rotation_quaternion = quaternion
    bpy.context.view_layer.update()


def solve_arm(rig, side, source, offset, frame):
    shoulder, old_elbow, wrist = [source[key] for key in ('shoulder', 'elbow', 'wrist')]
    upper_length = (old_elbow - shoulder).length
    lower_length = (wrist - old_elbow).length
    delta = wrist + offset - shoulder
    # Keep a bend in the elbow instead of stretching the arm to reach a target.
    distance = min(delta.length, upper_length + lower_length - .003)
    direction = delta.normalized()
    target = shoulder + direction * distance
    bend = old_elbow - shoulder - direction * (old_elbow - shoulder).dot(direction)
    along = (upper_length ** 2 - lower_length ** 2 + distance ** 2) / (2 * distance)
    elbow = shoulder + direction * along + bend.normalized() * math.sqrt(
        max(0, upper_length ** 2 - along ** 2))
    upper_rotation = (old_elbow - shoulder).rotation_difference(elbow - shoulder) @ source['upper'].to_quaternion()
    lower_rotation = (wrist - old_elbow).rotation_difference(target - elbow) @ source['lower'].to_quaternion()
    for part, rotation in [('Arm', upper_rotation), ('ForeArm', lower_rotation)]:
        bone = rig.pose.bones['mixamorig:' + side + part]
        set_rotation(bone, rotation)
        bone.keyframe_insert('rotation_quaternion', frame=frame)
    # The hand follows its forearm; no independent wrist/world rotation is set.


def continuous_quaternions(action):
    flips = 0
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                groups = {}
                for curve in bag.fcurves:
                    if curve.data_path.endswith('rotation_quaternion'):
                        groups.setdefault(curve.data_path, {})[curve.array_index] = curve
                for curves in groups.values():
                    previous = None
                    for index in range(len(curves[0].keyframe_points)):
                        keys = [curves[i].keyframe_points[index] for i in range(4)]
                        current = Quaternion(tuple(key.co.y for key in keys))
                        if previous is not None and current.dot(previous) < 0:
                            # q and -q represent exactly the same keyed pose.
                            # Use matching signs for smooth component interpolation.
                            for key in keys:
                                key.co.y = -key.co.y
                                key.handle_left.y = -key.handle_left.y
                                key.handle_right.y = -key.handle_right.y
                            current.negate()
                            flips += 1
                        previous = current
    return flips


def main():
    bpy.ops.wm.open_mainfile(filepath=str(BASELINE))
    scene = bpy.context.scene
    rig = next(obj for obj in scene.objects if obj.type == 'ARMATURE')
    report = {'status': 'Local review candidate; not artist-approved', 'clips': []}
    for name in REPAIRED:
        action = bpy.data.actions[name]
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        cache = {}
        for frame in range(1, int(action.frame_range[1]) + 1):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            cache[frame] = {side: arm_state(rig, side) for side in ('Right', 'Left')}
        changed = []
        for frame, states in cache.items():
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            for side in ('Right', 'Left'):
                offset = target_offset(name, frame, side)
                if offset.length > 0:
                    solve_arm(rig, side, states[side], offset, frame)
                    changed.append([frame, side])
        flips = continuous_quaternions(action)
        report['clips'].append({'name': name, 'changedArms': changed,
                                'equivalentQuaternionSignChanges': flips})
    action = bpy.data.actions['SwordAttack']
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    scene.frame_start, scene.frame_end = 1, 46
    scene.frame_set(27)
    scene['Candidate'] = 'Arin v5.8 local motion repair; awaiting Sin inspection'
    scene['Deferred'] = 'No commit or push authorized for this review candidate'
    scene.camera.data.shift_x = scene.camera.data.shift_y = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    (PACKAGE / 'Diagnostics/motion-repair-authoring.json').write_text(
        json.dumps(report, indent=2) + '\n', newline='\n')
    print('MOTION_REPAIR_BAKED', json.dumps(report['clips'][0]['changedArms']), flush=True)


if __name__ == '__main__':
    main()

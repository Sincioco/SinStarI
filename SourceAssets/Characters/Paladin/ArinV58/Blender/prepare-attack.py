"""Apply the artist's v5.8 Idle grip to raw primary Attack for Blender review.

Only creates a separate review scene. Never rebuilds the approved Idle checkpoint
or imports Studio calibration. Uses the same v5.8 motion retargeter as Idle.
"""
import bpy
import hashlib
import json
import runpy
from pathlib import Path
from mathutils import Matrix, Vector

PACKAGE = Path(__file__).resolve().parents[1]
CHECKPOINT = PACKAGE/'Blender/arin-v5.8-idle-approved.blend'
SOURCE = PACKAGE/'Source/arin-v5.8-primary-attack-motion.fbx'
OUTPUT = PACKAGE/'Blender/arin-v5.8-attack-review.blend'


def rows(matrix):
    return [list(row) for row in matrix]


def main():
    if OUTPUT.exists():
        raise RuntimeError('Preserve artist edits: Attack output already exists')
    owners = runpy.run_path(str(PACKAGE/'Blender/prepare-idle.py'))
    approved = json.loads((PACKAGE/'Diagnostics/idle-approved-grip.json').read_text())
    assert hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest() == approved['checkpointSha256']
    bpy.ops.wm.open_mainfile(filepath=str(CHECKPOINT))
    scene = bpy.context.scene
    scene.frame_set(approved['frame'])
    bpy.context.view_layer.update()
    rig = next(obj for obj in scene.objects if obj.type == 'ARMATURE')
    body = [obj for obj in scene.objects if obj.type == 'MESH'
            and obj.name.startswith('ArinV58.')]
    props = [bpy.data.objects[item['name']] for item in approved['equipment']]
    fingerprints = {obj.name: (rows(obj.matrix_basis), rows(obj.matrix_parent_inverse))
                    for obj in props}
    grip = {item['name']: Matrix(item['handRelativeMatrix']) for item in approved['equipment']}
    finger_pose = {bone.name: bone.rotation_quaternion.copy() for bone in rig.pose.bones
                   if not bone.name.startswith('mixamorig:')}
    idle_action = rig.animation_data.action
    idle_action.use_fake_user = True
    action = owners['load_motion'](rig, SOURCE, 'SwordAttack', finger_pose)
    scene.frame_set(scene.frame_start)
    bpy.context.view_layer.update()
    first_minimum = owners['minimum'](body)
    # A single measured clip placement; preserve the source's vertical motion.
    rig.location.z -= first_minimum
    bpy.context.view_layer.update()
    frame_checks = []
    max_drift = 0.0
    max_seam_gap = 0.0
    hands = [obj for obj in body if obj.name.endswith(('tripo_part_2','tripo_part_3'))]
    for frame in range(scene.frame_start, scene.frame_end+1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        for obj in props:
            assert fingerprints[obj.name] == (rows(obj.matrix_basis), rows(obj.matrix_parent_inverse))
            hand = rig.matrix_world @ rig.pose.bones[obj.parent_bone].matrix
            relative = hand.inverted() @ obj.matrix_world
            drift = max(abs(relative[r][c]-grip[obj.name][r][c])
                        for r in range(4) for c in range(4))
            max_drift = max(max_drift, drift)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for obj in hands:
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            seen = {}
            for original, posed in zip(obj.data.vertices, mesh.vertices):
                key = tuple(round(c, 6) for c in original.co)
                position = evaluated.matrix_world @ posed.co
                if key in seen:
                    max_seam_gap = max(max_seam_gap, (position-seen[key]).length)
                else:
                    seen[key] = position
            evaluated.to_mesh_clear()
        frame_checks.append({'frame':frame,'bodyMinimumZ':owners['minimum'](body)})
    # The new boot shape dips below the floor during the raw slash. Lift the
    # whole actor only on penetrating samples; keep intentional airborne motion
    # and the approved hand-relative equipment transforms unchanged.
    baseline_z = rig.location.z
    maximum_lift = 0.0
    for check in frame_checks:
        scene.frame_set(check['frame'])
        raw_minimum = check['bodyMinimumZ']
        lift = max(0.0, -raw_minimum)
        maximum_lift = max(maximum_lift, lift)
        rig.location.z = baseline_z + lift
        rig.keyframe_insert('location', index=2, frame=check['frame'])
        bpy.context.view_layer.update()
        check['bodyMinimumZBeforeContactRepair'] = raw_minimum
        check['bodyMinimumZ'] = owners['minimum'](body)
        assert check['bodyMinimumZ'] >= -.000001
        for obj in props:
            hand = rig.matrix_world @ rig.pose.bones[obj.parent_bone].matrix
            relative = hand.inverted() @ obj.matrix_world
            max_drift = max(max_drift, max(abs(relative[r][c]-grip[obj.name][r][c])
                                         for r in range(4) for c in range(4)))
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    if curve.data_path == 'location':
                        for key in curve.keyframe_points:
                            key.interpolation = 'LINEAR'
    assert max_drift < .00001, max_drift
    assert max_seam_gap < .00002, max_seam_gap
    scene.timeline_markers.clear()
    for name, frame in [('Start',1), ('Windup',12), ('Strike Review',22), ('Recovery',scene.frame_end)]:
        scene.timeline_markers.new(name, frame=frame)
    scene['Candidate'] = 'Arin v5.8 — primary Attack using Sin-corrected Idle grip'
    scene['Grip Checkpoint'] = 'arin-v5.8-idle-approved.blend'
    scene['Calibration'] = 'No v5.7 Studio calibrations imported'
    for obj in props:
        obj['Grip Status'] = 'Transferred unchanged from Sin-corrected Idle; Attack review pending'
    # Show a complete swing silhouette while keeping the equipment editable.
    camera = scene.camera
    camera.data.ortho_scale = 1.75
    target = Vector((0,0,.52))
    camera.location = Vector((.8,-2.8,1.05))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    for label, frame in [('Start',1), ('Strike',22), ('Recovery',scene.frame_end)]:
        scene.frame_set(frame)
        scene.render.filepath = str(PACKAGE/f'Previews/Attack-{label}.png')
        bpy.ops.render.render(write_still=True)
    scene.frame_set(22)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
                space.region_3d.view_location = target
                space.region_3d.view_distance = 2.15
                space.region_3d.view_perspective = 'ORTHO'
    bpy.ops.object.select_all(action='DESELECT')
    sword = next(obj for obj in props if obj.name.startswith('Sword'))
    sword.select_set(True)
    bpy.context.view_layer.objects.active = sword
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    report = {'clip':'SwordAttack', 'displayName':'Attack', 'source':SOURCE.name,
              'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'idleCheckpointSha256':approved['checkpointSha256'],
              'outputSha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              'frameRange':[scene.frame_start,scene.frame_end], 'reviewFrame':22,
              'bodyTriangles':sum(len(o.data.polygons) for o in body),
              'maximumHandRelativeMatrixDrift':max_drift,
              'maximumHandSeamGap':max_seam_gap,
              'firstBodyMinimumZBeforePlacement':first_minimum,
              'clipPlacementAdjustmentZ':-first_minimum,
              'maximumFloorContactLift':maximum_lift,
              'frames':frame_checks, 'equipmentLocalTransformsPreserved':True,
              'calibrationImported':False, 'artistAttackReview':'Pending'}
    (PACKAGE/'Diagnostics/attack-validation.json').write_text(json.dumps(report,indent=2))
    print('ATTACK_REVIEW='+json.dumps(report),flush=True)


if __name__ == '__main__':
    main()

"""Focused regression for the reported v5.8 limb/equipment intersections."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Quaternion
from mathutils.bvhtree import BVHTree

PACKAGE = Path(__file__).resolve().parents[1]
REPAIRED = ('SwordAttack', 'Victory', 'TownIdle')
PAIRS = [('right', 'legs'), ('left', 'legs'), ('sword', 'shield'),
         ('sword', 'legs'), ('shield', 'legs'), ('sword', 'torso'), ('shield', 'torso')]


def curves():
    return {(a.name, f.data_path, f.array_index):
            [(list(k.co), k.interpolation) for k in f.keyframe_points]
            for a in bpy.data.actions for layer in a.layers
            for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves}


def region(body, names):
    groups = {g.index for g in body.vertex_groups if any(name in g.name for name in names)}
    vertices = {v.index for v in body.data.vertices
                if sum(g.weight for g in v.groups if g.group in groups) > .5}
    return [tuple(t.vertices) for t in body.data.loop_triangles
            if all(i in vertices for i in t.vertices)]


def geometry_signature():
    result = {}
    for name in ('Body', 'Sword', 'Shield'):
        obj = bpy.data.objects[name]
        values = [(tuple(v.co), [(g.group, g.weight) for g in v.groups]) for v in obj.data.vertices]
        values += [tuple(p.vertices) for p in obj.data.polygons]
        result[name] = hashlib.sha256(repr(values).encode()).hexdigest()
    return result


def inspect(body, regions):
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    points = [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]
    trees = {name: BVHTree.FromPolygons(points, triangles, all_triangles=True)
             for name, triangles in regions.items()}
    floor = 100.0
    for name in ('Sword', 'Shield'):
        obj = bpy.data.objects[name]
        points = [obj.matrix_world @ v.co for v in obj.data.vertices]
        trees[name.lower()] = BVHTree.FromPolygons(points,
            [tuple(t.vertices) for t in obj.data.loop_triangles], all_triangles=True)
        if name == 'Sword':
            floor = min(v.z for v in points)
    return {a + '_' + b: len(trees[a].overlap(trees[b])) for a, b in PAIRS}, floor


def main():
    baseline = PACKAGE / 'Blender/arin-v5.8-approved-before-motion-repair.blend'
    candidate = PACKAGE / 'Blender/arin-v5.8-all-animations.blend'
    bpy.ops.wm.open_mainfile(filepath=str(baseline))
    original = curves()
    geometry = geometry_signature()
    attachments = {n: [list(row) for row in bpy.data.objects[n].matrix_basis]
                   for n in ('Sword', 'Shield')}
    bpy.ops.wm.open_mainfile(filepath=str(candidate))
    current = curves()
    assert current.keys() == original.keys()
    assert geometry_signature() == geometry, 'Mesh geometry or skin weights changed'
    assert attachments == {n: [list(row) for row in bpy.data.objects[n].matrix_basis]
                           for n in attachments}, 'Approved grip changed'
    protected_error = 0.0
    for key, old in original.items():
        clip, path, axis = key
        if clip not in REPAIRED or not path.endswith('rotation_quaternion'):
            assert current[key] == old, key
            continue
        if axis != 0:
            continue
        arm_changed = any('"mixamorig:' + side + bone + '"' in path
                          for side in ('Right', 'Left') for bone in ('Arm', 'ForeArm'))
        if clip == 'TownIdle' and 'Left' in path:
            arm_changed = False
        if arm_changed:
            continue
        for index in range(len(old)):
            before = Quaternion(tuple(original[(clip, path, i)][index][0][1] for i in range(4)))
            after = Quaternion(tuple(current[(clip, path, i)][index][0][1] for i in range(4)))
            protected_error = max(protected_error, 1 - abs(before.normalized().dot(after.normalized())))
    assert protected_error < 1e-6, protected_error
    scene = bpy.context.scene
    rig = next(obj for obj in scene.objects if obj.type == 'ARMATURE')
    body = bpy.data.objects['Body']
    for name in ('Body', 'Sword', 'Shield'):
        bpy.data.objects[name].data.calc_loop_triangles()
    regions = {'legs': region(body, ['UpLeg', 'Leg', 'Foot', 'Toe']),
               'torso': region(body, ['Spine', 'Neck', 'Head'])}
    for side, name in [('Right', 'right'), ('Left', 'left')]:
        regions[name] = region(body, [side + part for part in
            ('ForeArm', 'Hand', 'Pinky', 'Ring', 'Middle', 'Index', 'Thumb')])
    results = []
    for name in REPAIRED:
        action = bpy.data.actions[name]
        rig.animation_data.action = action
        rig.animation_data.action_slot = action.slots[0]
        rows = []
        for half in range(2, int(action.frame_range[1]) * 2 + 1):
            frame = half / 2
            scene.frame_set(int(frame), subframe=frame % 1)
            bpy.context.view_layer.update()
            collisions, floor = inspect(body, regions)
            rows.append({'frame': frame, **collisions, 'swordMinimumZ': floor})
        failures = [row for row in rows if any(row[a + '_' + b] for a, b in PAIRS)]
        results.append({'clip': name, 'samples': len(rows), 'failures': failures,
                        'minimumSwordZ': min(row['swordMinimumZ'] for row in rows)})
        print('COLLISION_CHECK', json.dumps(results[-1]), flush=True)
    report = {'candidateSha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
              'baselineSha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
              'geometryAndSkinWeightsUnchanged': True, 'approvedGripUnchanged': True,
              'protectedLocalRotationError': protected_error,
              'eightOtherActionsUnchanged': True, 'results': results,
              'method': 'Triangle BVH intersections, both forearm/hand regions versus legs; equipment versus legs, torso/head, and each other; 0.5-frame samples.'}
    (PACKAGE / 'Diagnostics/motion-repair-validation.json').write_text(
        json.dumps(report, indent=2) + '\n', newline='\n')
    assert all(not item['failures'] for item in results), results
    assert all(item['minimumSwordZ'] > 0 for item in results), results
    print('MOTION_CLEARANCE_PASS', flush=True)


if __name__ == '__main__':
    main()

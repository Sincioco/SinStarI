"""Focused regression for the observed stiff legs, contacts and baked playback."""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from animate import CLIPS, LOOPS, foot_cycle

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps = 30
bpy.ops.import_scene.gltf(filepath=str(PACKAGE / 'red-dragon-v1.3-animated.glb'))
scene = bpy.context.scene
scene.render.fps = 30
rig = next(o for o in scene.objects if o.type == 'ARMATURE')
body = next(o for o in scene.objects if o.type == 'MESH')
actions = {a.name: a for a in bpy.data.actions}
assert set(actions) == set(CLIPS), list(actions)
assert len(rig.data.bones) == 28, len(rig.data.bones)
groups = {g.index: g.name for g in body.vertex_groups}
feet = {limb: [v.index for v in body.data.vertices if any(
    groups[g.group] == 'Paw_' + limb and g.weight > .999 for g in v.groups)]
    for limb in ('FrontL', 'FrontR', 'HindL', 'HindR')}
assert all(feet.values())
report = {'modelSha256': hashlib.sha256((PACKAGE / 'red-dragon-v1.3-animated.glb').read_bytes()).hexdigest(),
          'sampleRate': 30, 'axes': 'Blender Z up (SM3D Y up)', 'clips': {}, 'issues': []}
for name, action in actions.items():
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    first, last = (round(v) for v in action.frame_range)
    frames = []
    all_min = 100
    first_min = None
    foot_min = {limb: 100 for limb in feet}
    positions = []
    for frame in range(first, last + 1):
        scene.frame_set(frame)
        deps = bpy.context.evaluated_depsgraph_get()
        evaluated = body.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        pts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        assert all(math.isfinite(c) for p in pts for c in p), (name, frame)
        all_min = min(all_min, min(p.z for p in pts))
        if first_min is None:
            first_min = min(p.z for p in pts)
        for limb, indices in feet.items():
            foot_min[limb] = min(foot_min[limb], min(pts[i].z for i in indices))
        erig = rig.evaluated_get(deps)
        positions.append({limb: list(erig.matrix_world @ erig.pose.bones['Paw_' + limb].head)
                          for limb in feet})
        if frame in (first, last):
            frames.append(pts)
        evaluated.to_mesh_clear()
    seam = max((a - b).length for a, b in zip(*frames))
    span = {limb: max((Vector(p[limb]) - Vector(positions[0][limb])).length
                     for p in positions) for limb in feet}
    check = {'frames': len(positions), 'minimumZ': all_min, 'firstFrameMinimumZ': first_min,
             'firstFrameFeet': positions[0],
             'footMinimumZ': foot_min, 'footMotionSpan': span, 'loopSeamMaxDistance': seam}
    if all_min < -.004:
        report['issues'].append(f'{name}: floor penetration {all_min:.6f}')
    if name in LOOPS and seam > .0001:
        report['issues'].append(f'{name}: loop seam {seam:.6f}')
    if name not in ('Walk', 'Run'):
        planted = [v for k, v in span.items() if name != 'ClawStrike' or k != 'FrontR']
        check['plantedFootMaxDrift'] = max(planted)
        if max(planted) > .002:
            report['issues'].append(f'{name}: planted foot drift {max(planted):.6f}')
    else:
        expected_phases = ({'HindL': 0, 'HindR': .08, 'FrontL': .48, 'FrontR': .56}
                           if name == 'Run' else {'HindL': 0, 'FrontL': .25, 'HindR': .5, 'FrontR': .75})
        stride, duty, lift = (.18, .5, .065) if name == 'Run' else (.12, .72, .038)
        maximum = 0
        for limb, phase in expected_phases.items():
            y0, z0 = foot_cycle(phase, stride, duty, lift)
            p0 = Vector(positions[0][limb])
            for i, p in enumerate(positions):
                y, z = foot_cycle(i / (len(positions) - 1) + phase, stride, duty, lift)
                expected = p0 + Vector((0, y - y0, z - z0))
                maximum = max(maximum, (Vector(p[limb]) - expected).length)
        check['footPathMaxError'] = maximum
        if maximum > .002:
            report['issues'].append(f'{name}: foot path error {maximum:.6f}')
    report['clips'][name] = check
report['passed'] = not report['issues']
(PACKAGE / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'issues': report['issues'],
                  'clips': {n: {'floor': c['minimumZ'], 'seam': c['loopSeamMaxDistance'],
                     'path': c.get('footPathMaxError'), 'plant': c.get('plantedFootMaxDrift')}
                     for n, c in report['clips'].items()}}, indent=2))
assert report['passed'], report['issues']

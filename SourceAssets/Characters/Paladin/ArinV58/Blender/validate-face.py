"""Regression: both lower cheeks follow Head, with protected head/neck motion."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree

PACKAGE = Path(__file__).resolve().parents[1]


def signature(action):
    curves = []
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    if not any('"mixamorig:' + bone + '"' in curve.data_path
                               for bone in ('Head', 'Neck')):
                        continue
                    curves.append((curve.data_path, curve.array_index,
                        [(list(k.co), k.interpolation) for k in curve.keyframe_points]))
    return hashlib.sha256(json.dumps(sorted(curves)).encode()).hexdigest()


bpy.ops.wm.open_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-idle-approved.blend'))
face = bpy.data.objects['ArinV58.tripo_part_12']
points = [v.co.copy() for v in face.data.vertices if v.co.z >= .852]
bpy.ops.wm.open_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-attack-review.blend'))
original = signature(bpy.data.actions['SwordAttack'])
bpy.ops.wm.open_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-all-animations.blend'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
body = bpy.data.objects['Body']
tree = KDTree(len(body.data.vertices))
for v in body.data.vertices:
    tree.insert(v.co, v.index)
tree.balance()
indices = [tree.find(p)[1] for p in points]
assert max(tree.find(p)[2] for p in points) < 1e-6
head = rig.data.bones['mixamorig:Head']
head_group = body.vertex_groups['mixamorig:Head'].index
assert all(len(body.data.vertices[i].groups) == 1 and
           body.data.vertices[i].groups[0].group == head_group and
           abs(body.data.vertices[i].groups[0].weight-1) < 1e-6 for i in indices)
action = bpy.data.actions['SwordAttack']
assert signature(action) == original
rig.animation_data.action = action
rig.animation_data.action_slot = action.slots[0]
scene = bpy.context.scene
errors = []
for frame in range(1, 47):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    transform = rig.matrix_world @ rig.pose.bones[head.name].matrix @ head.matrix_local.inverted()
    error = max((evaluated.matrix_world @ evaluated.data.vertices[i].co -
                 transform @ (rig.matrix_world.inverted() @ body.matrix_world @ p)).length
                for p, i in zip(points, indices))
    errors.append({'frame':frame, 'maximumHeadRelativeError':error})
assert max(e['maximumHeadRelativeError'] for e in errors) < 1e-5
report = {'faceVertices':len(indices), 'bothSidesChecked':True,
          'attackHeadNeckCurvesUnchanged':True, 'headNeckCurveSha256':original, 'frames':errors}
(PACKAGE/'Diagnostics/face-regression.json').write_text(json.dumps(report, indent=2))
scene.render.engine = 'CYCLES'
scene.cycles.samples = 16
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
camera = scene.camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = .27
for frame in (11,28,38):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    deform = rig.matrix_world @ rig.pose.bones[head.name].matrix @ head.matrix_local.inverted()
    target = deform @ Vector((0,-.002,.895))
    for side in (-1,1):
        camera.location = target + deform.to_3x3() @ Vector((side*.48,-.7,.12))
        camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath = str(PACKAGE/f'Previews/Face-{frame}-{side}.png')
        bpy.ops.render.render(write_still=True)
print('FACE_REGRESSION_PASS='+json.dumps({k:v for k,v in report.items() if k!='frames'}))

"""Skin the approved textured mesh; bake grounded Idle/Walk for the armory scene."""
import hashlib
import json
import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'Source/Garran-Textured-T-Pose.glb'))
mesh = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
low = min(v.co.z for v in mesh.data.vertices)
height = max(v.co.z for v in mesh.data.vertices) - low
for v in mesh.data.vertices:
    v.co.z -= low
    v.co *= 1.8 / height
mesh.name = 'Garran'
bm = bmesh.new()
bm.from_mesh(mesh.data)
degenerate = [f for f in bm.faces if f.calc_area() < 1e-9]
removed = len(degenerate)
bmesh.ops.delete(bm, geom=degenerate, context='FACES_ONLY')
bm.to_mesh(mesh.data)
bm.free()

armature = bpy.data.armatures.new('Garran Skeleton')
rig = bpy.data.objects.new('Garran Rig', armature)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')

def bone(name, head, tail, parent=None):
    b = armature.edit_bones.new(name)
    b.head, b.tail = head, tail
    if parent:
        b.parent = armature.edit_bones[parent]

bone('Root', (0, 0, 0), (0, 0, .18))
bone('Hips', (0, 0, .9), (0, 0, 1.07), 'Root')
bone('Chest', (0, 0, 1.07), (0, 0, 1.42), 'Hips')
bone('Head', (0, 0, 1.46), (0, 0, 1.77), 'Chest')
for side, suffix in [(1, 'L'), (-1, 'R')]:
    bone('Arm'+suffix, (side*.225, 0, 1.425), (side*.505, 0, 1.405), 'Chest')
    bone('Forearm'+suffix, (side*.505, 0, 1.405), (side*.805, 0, 1.4), 'Arm'+suffix)
    bone('Hand'+suffix, (side*.805, 0, 1.4), (side*.975, 0, 1.4), 'Forearm'+suffix)
    bone('Thigh'+suffix, (side*.135, 0, .89), (side*.155, 0, .47), 'Hips')
    bone('Shin'+suffix, (side*.155, 0, .47), (side*.17, 0, .08), 'Thigh'+suffix)
bpy.ops.object.mode_set(mode='OBJECT')
groups = {b.name: mesh.vertex_groups.new(name=b.name) for b in armature.bones}

def blend(value, a, b):
    t = max(0, min(1, (value-a)/(b-a)))
    return t*t*(3-2*t)

def pair(a, b, t):
    return {a: 1-t, b: t}

for v in mesh.data.vertices:
    x, y, z = v.co
    suffix = 'L' if x >= 0 else 'R'
    ax = abs(x)
    if z > 1.48 and ax < .24:
        weights = pair('Chest', 'Head', blend(z, 1.46, 1.53))
    elif ax > .23 and z > 1.25:
        if ax < .35:
            weights = pair('Chest', 'Arm'+suffix, blend(ax, .23, .35))
        elif ax < .59:
            weights = pair('Arm'+suffix, 'Forearm'+suffix, blend(ax, .46, .56))
        else:
            weights = pair('Forearm'+suffix, 'Hand'+suffix, blend(ax, .77, .84))
    elif z >= .91:
        weights = pair('Hips', 'Chest', blend(z, 1.01, 1.22))
    elif z > .75:
        weights = pair('Thigh'+suffix, 'Hips', blend(z, .78, .94))
    else:
        weights = pair('Shin'+suffix, 'Thigh'+suffix, blend(z, .40, .56))
    for name, weight in weights.items():
        if weight > 0:
            groups[name].add([v.index], weight, 'REPLACE')
modifier = mesh.modifiers.new('Garran Skin', 'ARMATURE')
modifier.object = rig
mesh.parent = rig
scene = bpy.context.scene
scene.render.fps = 30
rig.animation_data_create()
records = {}

def rotate(name, axis, angle):
    basis = armature.bones[name].matrix_local.to_3x3()
    rotation = basis.inverted() @ Matrix.Rotation(angle, 3, axis) @ basis
    rig.pose.bones[name].rotation_quaternion = rotation.to_quaternion()

for clip, frames in [('Idle', 60), ('Walk', 32)]:
    action = bpy.data.actions.new(clip)
    rig.animation_data.action = action
    minima = []
    for frame in range(frames+1):
        scene.frame_set(frame)
        phase = frame / frames * math.tau
        for p in rig.pose.bones:
            p.rotation_mode = 'QUATERNION'
            p.rotation_quaternion = Quaternion()
            p.location = (0, 0, 0)
        rotate('Chest', 'X', .008*math.sin(phase))
        rotate('Head', 'Z', .012*math.sin(phase))
        for side, suffix in [(1, 'L'), (-1, 'R')]:
            p = rig.pose.bones['Arm'+suffix]
            basis = armature.bones[p.name].matrix_local.to_3x3()
            swing = .10*side*math.sin(phase) if clip == 'Walk' else .012*math.sin(phase)
            rotation = Matrix.Rotation(swing, 3, 'X') @ Matrix.Rotation(side*1.34, 3, 'Y')
            p.rotation_quaternion = (basis.inverted() @ rotation @ basis).to_quaternion()
            if clip == 'Walk':
                rotate('Thigh'+suffix, 'X', side*.22*math.sin(phase))
                rotate('Shin'+suffix, 'X', -.28*max(0, side*math.sin(phase)))
        bpy.context.view_layer.update()
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        posed = evaluated.to_mesh()
        minimum = min(v.co.z for v in posed.vertices)
        evaluated.to_mesh_clear()
        # Root local Y is world Z for the vertical root bone.
        rig.pose.bones['Root'].location.y = -minimum
        bpy.context.view_layer.update()
        evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        posed = evaluated.to_mesh()
        minima.append(min(v.co.z for v in posed.vertices))
        evaluated.to_mesh_clear()
        for p in rig.pose.bones:
            p.keyframe_insert('rotation_quaternion', frame=frame, group=p.name)
            p.keyframe_insert('location', frame=frame, group=p.name)
    records[clip] = {'frames': frames+1, 'minimumY': min(minima), 'maximumMinimumY': max(minima), 'frameZeroY': minima[0]}
    assert max(abs(v) for v in minima) < .0001, records[clip]
    rig.animation_data.action = None
    track = rig.animation_data.nla_tracks.new()
    track.name = clip
    track.strips.new(clip, 0, action)
    track.mute = True

for image in bpy.data.images:
    if image.size[0] > 0:
        image.pack()
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
scene.frame_start, scene.frame_end = 0, 60
scene.frame_set(0)
bpy.ops.export_scene.gltf(filepath=str(ROOT / 'Garran.glb'), export_format='GLB', use_selection=True,
    export_animations=True, export_animation_mode='ACTIONS', export_force_sampling=True,
    export_nla_strips=True, export_skins=True, export_all_influences=False)
rig.animation_data.action = bpy.data.actions['Idle']
scene.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'Garran.blend'))
report = {'name': 'Garran', 'role': 'Neris Town weapon shop owner', 'heightMeters': 1.8,
    'bindMinimumY': min(v.co.z for v in mesh.data.vertices), 'triangles': sum(len(p.vertices)-2 for p in mesh.data.polygons),
    'bones': len(armature.bones), 'materials': len(mesh.data.materials), 'removedDegenerateTriangles': removed, 'clips': records,
    'sha256': hashlib.sha256((ROOT / 'Garran.glb').read_bytes()).hexdigest()}
(ROOT / 'grounding.json').write_text(json.dumps(report, indent=2)+'\n')
(ROOT / 'garran.sm3d.json').write_text(json.dumps({'version': 1, 'sampleRate': 30,
    'clips': {'Idle': {'loop': True}, 'Walk': {'loop': True}}}, indent=2)+'\n')
print(json.dumps(report))

"""Build the editable IK rig and baked Studio GLB from the preserved v1.1 mesh.

Run in installed Blender: blender --background --python <this file>.
Only this revision's outputs are replaced; the earlier packages are read-only.
"""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from animate import CLIPS, LOOPS, pose

SOURCE = PACKAGE / 'Source'
if not globals().get('SOURCE_ALREADY_OPEN', False):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE / 'red-dragon-v1.1-rig.blend'))
rig = bpy.data.objects['RedDragonRig']
body = bpy.data.objects['RedDragonBody']
scene = bpy.context.scene
scene.render.fps = 30
rig.hide_set(False)
rig.animation_data_clear()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
for b in rig.pose.bones:
    b.matrix_basis = Matrix.Identity(4)

def geometry_hash():
    data = {'vertices': [list(v.co) for v in body.data.vertices],
            'faces': [list(f.vertices) for f in body.data.polygons],
            'uv': [list(v.uv) for v in body.data.uv_layers.active.data]}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

original_hash = geometry_hash()
original_floor = min(v.co.z for v in body.data.vertices)
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
limbs = {}
for region in ('Front', 'Hind'):
    for side in ('L', 'R'):
        limb = region + side
        upper = rig.data.edit_bones[region + 'Leg' + side]
        lower = rig.data.edit_bones[region + 'Foot' + side]
        if region == 'Front':
            upper.parent = rig.data.edit_bones['Chest']
        ankle = lower.tail.copy()
        paw = rig.data.edit_bones.new('Paw_' + limb)
        paw.head = ankle
        paw.tail = ankle + Vector((0, -.07, 0))
        paw.parent = lower
        control = rig.data.edit_bones.new('IK_' + limb)
        control.head = ankle
        control.tail = paw.tail
        control.use_deform = False
        axis = (ankle - upper.head).normalized()
        bend = lower.head - upper.head
        bend = (bend - axis * bend.dot(axis)).normalized()
        pole = rig.data.edit_bones.new('Pole_' + limb)
        pole.head = lower.head + bend * .22
        pole.tail = pole.head + Vector((0, 0, .06))
        pole.use_deform = False
        # Blender's pole angle is relative to the upper bone's local X axis.
        normal = (ankle - upper.head).cross(pole.head - upper.head)
        projected = normal.cross(upper.tail - upper.head).normalized()
        angle = upper.x_axis.angle(projected)
        if upper.x_axis.cross(projected).dot(upper.tail - upper.head) > 0:
            angle = -angle
        limbs[limb] = {'poleAngle': angle, 'ankle': list(ankle)}
bpy.ops.object.mode_set(mode='OBJECT')

# The low claws get independent, level paws; knee/ankle transitions stay smooth.
for limb in limbs:
    region, side = limb[:-1], limb[-1]
    old = body.vertex_groups[region + 'Foot' + side]
    paw_group = body.vertex_groups.new(name='Paw_' + limb)
    for vertex in body.data.vertices:
        weight = next((g.weight for g in vertex.groups if g.group == old.index), 0)
        mix = max(0, min(1, (.105 - vertex.co.z) / .045))
        mix = mix * mix * (3 - 2 * mix)
        if weight * mix > 0:
            paw_group.add([vertex.index], weight * mix, 'REPLACE')
            old.add([vertex.index], weight * (1 - mix), 'REPLACE')
    lower = rig.pose.bones[region + 'Foot' + side]
    ik = lower.constraints.new('IK')
    ik.name = 'Planted Foot / Two Bone IK'
    ik.target = rig
    ik.subtarget = 'IK_' + limb
    ik.pole_target = rig
    ik.pole_subtarget = 'Pole_' + limb
    ik.pole_angle = limbs[limb]['poleAngle']
    ik.chain_count = 2
    ik.use_stretch = False
    ik.iterations = 100
    paw = rig.pose.bones['Paw_' + limb]
    level = paw.constraints.new('COPY_ROTATION')
    level.name = 'Level Claws'
    level.target = rig
    level.subtarget = 'IK_' + limb
    level.target_space = 'WORLD'
    level.owner_space = 'WORLD'
    for name in (region + 'Leg' + side, region + 'Foot' + side):
        rig.pose.bones[name].ik_stretch = 0
    rig.data.bones['IK_' + limb].color.palette = 'THEME04'
    rig.data.bones['Pole_' + limb].color.palette = 'THEME03'

assert geometry_hash() == original_hash, 'Rig edits changed original geometry/UVs'
rig.animation_data_create()
bakes = {}
actions = {}
for name, last in CLIPS.items():
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    rig.animation_data.action = action
    for frame in range(last + 1):
        scene.frame_set(frame + 1)
        pose(rig, name, frame / 30, last / 30)
        for b in rig.pose.bones:
            b.keyframe_insert('location', frame=frame + 1, group=b.name)
            b.keyframe_insert('rotation_quaternion', frame=frame + 1, group=b.name)
    # Every baked frame has exact authored timing; interpolation must not overshoot.
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points:
                        key.interpolation = 'LINEAR'
    actions[name] = action
    frames = []
    for frame in range(last + 1):
        scene.frame_set(frame + 1)
        bpy.context.view_layer.update()
        evaluated = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
        matrices = {b.name: b.matrix.copy() for b in evaluated.pose.bones}
        bases = {}
        for b in rig.data.bones:
            bases[b.name] = b.convert_local_to_pose(matrices[b.name], b.matrix_local,
                parent_matrix=matrices[b.parent.name] if b.parent else Matrix.Identity(4),
                parent_matrix_local=b.parent.matrix_local if b.parent else Matrix.Identity(4),
                invert=True)
        frames.append(bases)
    bakes[name] = frames

rig.animation_data.action = actions['Walk']
rig.animation_data.action_slot = actions['Walk'].slots[0]
scene.frame_start, scene.frame_end = 1, 61
scene.frame_set(1)
rig.show_in_front = True
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            space.shading.type = 'MATERIAL'
            space.overlay.show_overlays = False
            space.region_3d.view_distance = 2.3
            space.region_3d.view_location = (0, -.1, .28)
            space.region_3d.view_rotation = Vector((1.4, -1.8, .7)).to_track_quat('Z', 'Y')
bpy.ops.wm.save_as_mainfile(filepath=str(PACKAGE / 'red-dragon-v1.3-rig.blend'), compress=True)

# Save the live control rig first; export a constraint-free baked copy in memory.
rig.animation_data_clear()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)
for b in rig.pose.bones:
    for constraint in list(b.constraints):
        b.constraints.remove(constraint)
rig.animation_data_create()
for name, frames in bakes.items():
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    rig.animation_data.action = action
    previous = {}
    for frame, bases in enumerate(frames, 1):
        for b in rig.pose.bones:
            b.matrix_basis = bases[b.name]
            b.rotation_mode = 'QUATERNION'
            if b.name in previous and b.rotation_quaternion.dot(previous[b.name]) < 0:
                b.rotation_quaternion.negate()
            previous[b.name] = b.rotation_quaternion.copy()
            b.keyframe_insert('location', frame=frame, group=b.name)
            b.keyframe_insert('rotation_quaternion', frame=frame, group=b.name)
            b.keyframe_insert('scale', frame=frame, group=b.name)

bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
body.select_set(True)
bpy.context.view_layer.objects.active = rig
model = PACKAGE / 'red-dragon-v1.3-animated.glb'
bpy.ops.export_scene.gltf(filepath=str(model), export_format='GLB', use_selection=True,
    export_materials='EXPORT', export_animations=True, export_animation_mode='ACTIONS',
    export_merge_animation='ACTION', export_anim_single_armature=True,
    export_armature_object_remove=True, export_rest_position_armature=True,
    export_reset_pose_bones=False, export_optimize_animation_keep_anim_armature=False,
    export_extra_animations=False, export_skins=True, export_def_bones=True,
    export_anim_slide_to_zero=True)
descriptor = json.loads((SOURCE / 'RedDragonV11.sm3d.json').read_text())
descriptor['clips'] = {name: {'loop': name in LOOPS} for name in CLIPS}
(PACKAGE / 'RedDragonV13.sm3d.json').write_text(json.dumps(descriptor, indent=2) + '\n')
manifest = {'version': '1.3', 'source': 'Source/red-dragon-v1.1-rig.blend',
    'sourceSha256': hashlib.sha256((SOURCE / 'red-dragon-v1.1-rig.blend').read_bytes()).hexdigest(),
    'modelSha256': hashlib.sha256(model.read_bytes()).hexdigest(),
    'geometryUvSha256': original_hash, 'geometryChanged': False,
    'bindMinimumZ': original_floor, 'sampleRate': 30, 'runtimeScalePercent': 25000,
    'deformBones': 28, 'controlBones': 8, 'clips': CLIPS, 'footControls': limbs,
    'locomotion': {'Walk': {'stride': .12, 'seconds': 2, 'stanceFraction': .72},
                   'Run': {'stride': .18, 'seconds': 1, 'stanceFraction': .5}},
    'attackCuesSeconds': {'ClawStrike': 1, 'FireBreath': [.85, 3.1], 'Fireball': 1.8}}
(PACKAGE / 'package.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('DRAGON V1.3: live IK rig and eight baked clips exported')

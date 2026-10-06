"""Export the review scene with 2K equipment maps for the native texture budget."""
import bpy
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from finalize_export import finalize_export

bpy.ops.wm.open_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-all-animations.blend'))
images = set()
for slot in bpy.data.objects['Sword'].material_slots:
    if slot.material and slot.material.use_nodes:
        images.update(n.image for n in slot.material.node_tree.nodes
                      if n.type == 'TEX_IMAGE' and n.image)
report = []
for image in images:
    original = list(image.size)
    if max(original) > 2048:
        factor = 2048/max(original)
        image.scale(round(original[0]*factor), round(original[1]*factor))
    report.append({'image':image.name, 'sourceSize':original, 'runtimeSize':list(image.size)})
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
body = bpy.data.objects['Body']
# Native character assets require one skin on every part. Bake each rigid prop
# into body bind space and weight it wholly to its approved hand bone. The
# review scene remains bone-parented and editable; only the export is changed.
rig.data.pose_position = 'REST'
bpy.context.view_layer.update()
for name, bone in [('Shield','mixamorig:LeftHand'),('Sword','mixamorig:RightHand')]:
    obj = bpy.data.objects[name]
    bind = body.matrix_world.inverted() @ obj.matrix_world
    obj.data.transform(bind)
    obj.parent = body.parent
    obj.parent_type = 'OBJECT'
    obj.parent_bone = ''
    obj.matrix_parent_inverse = body.matrix_parent_inverse.copy()
    obj.matrix_basis = body.matrix_basis.copy()
    obj.vertex_groups.clear()
    group = obj.vertex_groups.new(name=bone)
    group.add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
    modifier = obj.modifiers.new('Native Skin', 'ARMATURE')
    modifier.object = rig
rig.data.pose_position = 'POSE'
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for obj in [rig, bpy.data.objects['Body'], bpy.data.objects['Sword'], bpy.data.objects['Shield']]:
    obj.select_set(True)
bpy.context.view_layer.objects.active = rig
output = PACKAGE/'arin-v5.8-animation-checkpoint.glb'
bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB', use_selection=True,
    export_animations=True, export_animation_mode='ACTIONS', export_merge_animation='ACTION',
    export_anim_single_armature=True, export_rest_position_armature=True,
    export_reset_pose_bones=False, export_skins=True, export_tangents=True)
finalize_export(output)
(PACKAGE/'Diagnostics/runtime-textures.json').write_text(json.dumps(report, indent=2))

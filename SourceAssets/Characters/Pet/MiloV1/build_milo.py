"""Rebuild Milo's original canine rig with the installed Blender, in background.

Run: blender --background --python-exit-code 1 --python <this file>
Only this package's generated files are replaced; the Tripo original is retained.
"""
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from milo_motion import build_actions


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(next((ROOT / 'Original').glob('*.fbx'))))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert len(meshes) == 1
    body = meshes[0]
    body.name = 'MiloBody'
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    floor = min(v.co.z for v in body.data.vertices)
    for vertex in body.data.vertices:
        vertex.co.z -= floor
    triangles = sum(len(p.vertices) - 2 for p in body.data.polygons)
    assert triangles == 9502
    for material in body.data.materials:
        shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        shader.inputs['Roughness'].default_value = .72
        shader.inputs['Metallic'].default_value = 0
    for polygon in body.data.polygons:
        polygon.use_smooth = True

    bpy.ops.object.armature_add()
    rig = bpy.context.object
    rig.name = 'MiloRig'
    rig.data.name = 'MiloSkeleton'
    rig.show_in_front = True
    bpy.ops.object.mode_set(mode='EDIT')
    rig.data.edit_bones.remove(rig.data.edit_bones[0])
    specs = {}

    def bone(name, head, tail, parent=None, deform=True):
        b = rig.data.edit_bones.new(name)
        b.head, b.tail, b.use_deform = head, tail, deform
        if parent:
            b.parent = rig.data.edit_bones[parent]
        specs[name] = dict(head=list(head), tail=list(tail), parent=parent)

    bone('Root', (0, 0, .44), (0, -.08, .44), deform=False)
    bone('Pelvis', (0, .28, .49), (0, .13, .52), 'Root')
    bone('Spine', (0, .13, .52), (0, -.08, .54), 'Pelvis')
    bone('Chest', (0, -.08, .54), (0, -.23, .59), 'Spine')
    bone('Neck', (0, -.23, .59), (0, -.28, .71), 'Chest')
    bone('Head', (0, -.28, .71), (0, -.40, .74), 'Neck')
    bone('Tail1', (0, .34, .54), (0, .395, .39), 'Pelvis')
    bone('Tail2', (0, .395, .39), (0, .43, .24), 'Tail1')
    bone('Tail3', (0, .43, .24), (0, .49, .16), 'Tail2')
    for side, sign in [('L', 1), ('R', -1)]:
        x = .105 * sign
        bone('Ear' + side, (sign*.092, -.258, .824), (sign*.132, -.285, .762), 'Head')
        bone('FrontUpper' + side, (x, -.215, .48), (x, -.19, .285), 'Chest')
        bone('FrontLower' + side, (x, -.19, .285), (x, -.23, .072), 'FrontUpper' + side)
        bone('FrontPaw' + side, (x, -.23, .072), (x, -.305, .025), 'FrontLower' + side)
        bone('HindUpper' + side, (x, .27, .47), (x, .18, .30), 'Pelvis')
        bone('HindLower' + side, (x, .18, .30), (x, .33, .135), 'HindUpper' + side)
        bone('HindAnkle' + side, (x, .33, .135), (x, .32, .065), 'HindLower' + side)
        bone('HindPaw' + side, (x, .32, .065), (x, .245, .025), 'HindAnkle' + side)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Heat weights follow the connected surface, avoiding an arbitrary spatial split
    # through the neck, armored shoulders or tail. Export accepts four influences.
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    unweighted = []
    for vertex in body.data.vertices:
        influences = sorted([(g.group, g.weight) for g in vertex.groups if g.weight > 1e-5],
                            key=lambda v: v[1], reverse=True)[:4]
        if not influences:
            unweighted.append(vertex.index)
            continue
        for group in body.vertex_groups:
            group.remove([vertex.index])
        total = sum(w for _, w in influences)
        for index, weight in influences:
            body.vertex_groups[index].add([vertex.index], weight / total, 'REPLACE')
    # Tripo contains detached fur/armor islands. Transfer skin from the closest
    # weighted surface on those islands; preserve geometry, normals and UVs.
    weighted = [v for v in body.data.vertices if len(v.groups)]
    tree = KDTree(len(weighted))
    for vertex in weighted:
        tree.insert(vertex.co, vertex.index)
    tree.balance()
    for index in unweighted:
        _, nearest, distance = tree.find(body.data.vertices[index].co)
        assert distance < .07, ('Detached island too far from skin', index, distance)
        for influence in body.data.vertices[nearest].groups:
            body.vertex_groups[influence.group].add([index], influence.weight, 'REPLACE')
    assert all(len(v.groups) for v in body.data.vertices)
    for pose in rig.pose.bones:
        pose.rotation_mode = 'QUATERNION'

    actions, validation = build_actions(rig, body)
    bpy.context.scene.frame_set(1)
    rig.animation_data.action = actions[0]
    rig.animation_data.action_slot = actions[0].slots[0]
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    output = ROOT / 'milo-v1-animated.glb'
    bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB', use_selection=True,
        export_materials='EXPORT', export_animations=True, export_animation_mode='ACTIONS',
        export_merge_animation='ACTION', export_anim_single_armature=True,
        export_armature_object_remove=True, export_rest_position_armature=True,
        export_anim_slide_to_zero=True, export_optimize_animation_size=False,
        export_reset_pose_bones=False, export_optimize_animation_keep_anim_armature=False,
        export_extra_animations=False, export_skins=True)
    sockets = {name: {'node': name, 'translation': [0, 0, 0]}
               for name in ['Root', 'Chest', 'Head', 'FrontPawL', 'FrontPawR', 'HindPawL', 'HindPawR', 'Tail3']}
    descriptor = {'version': 1, 'sampleRate': 30,
                  'clips': {a.name: {'loop': a.name in ['Idle', 'Walk', 'Run']} for a in actions},
                  'sockets': sockets}
    write_json('MiloV1.sm3d.json', descriptor)
    write_json('grounding-and-motion.json', validation)
    for image in bpy.data.images:
        if image.source == 'FILE':
            image.pack()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.shading.type = 'MATERIAL'
                area.spaces.active.region_3d.view_distance = 1.7
                area.spaces.active.region_3d.view_location = (0, 0, .42)
                area.spaces.active.region_3d.view_rotation = Vector((1, -2, .7)).to_track_quat('Z', 'Y')
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 91
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'milo-v1-rig.blend'), compress=True)
    manifest = {'version': '1.0', 'status': 'Candidate, awaiting Sin animation review',
                'source': 'Original/Milo - 4K - Low Poly - No Lighting.zip',
                'builder': 'build_milo.py', 'motionSource': 'Original authored canine actions in milo_motion.py',
                'vertices': len(body.data.vertices), 'triangles': triangles, 'geometryChanged': False,
                'textureSize': [4096, 4096], 'detachedVerticesWeightTransferred': len(unweighted),
                'bones': specs, 'clips': list(descriptor['clips']),
                'blenderVersion': bpy.app.version_string, 'modelSha256': sha(output)}
    write_json('milo-v1-package.json', manifest)
    print('MILO RIG PASS', len(specs), 'bones,', len(actions), 'actions,', triangles, 'triangles')


def write_json(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


if __name__ == '__main__':
    build()

"""Prepare the isolated v5.8 inspection rig; never read Studio calibrations.

Run with installed Blender in background. This is a candidate skin transfer,
not an accepted replacement for Arin v5.7. Equipment remains directly editable.
"""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import barycentric_transform

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sword_geometry import straighten_sword


def imported(path):
    before = set(bpy.data.objects)
    if path.suffix == '.blend':
        # Authored TownIdle must retain its original rest basis. An FBX-only
        # armature export promoted the relaxed pose to rest and erased its delta.
        with bpy.data.libraries.load(str(path), link=False) as (source, target):
            target.objects = source.objects
        for obj in target.objects:
            bpy.context.collection.objects.link(obj)
    elif path.suffix == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        bpy.ops.import_scene.gltf(filepath=str(path))
    return [obj for obj in bpy.data.objects if obj not in before]


def action_for(rig, action):
    rig.animation_data_create()
    rig.animation_data.action = action
    if action and action.slots:
        rig.animation_data.action_slot = action.slots[0]


def normalize(rig, action):
    factor = rig.scale.x
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if action:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        if curve.data_path.endswith('.location'):
                            for key in curve.keyframe_points:
                                key.co.y *= factor
                                key.handle_left.y *= factor
                                key.handle_right.y *= factor


def fit_point(point):
    """Candidate-specific anatomical fit; leaves the new body unchanged."""
    x, y, z = point
    x -= 0.02788689
    # The reference has a wider stance and slightly shorter arm span.
    blend = min(1.0, max(0.0, (z - 0.60) / 0.17))
    x *= 0.76 + 0.35 * blend
    y -= 0.019 + max(0.0, z - 0.82) * 0.16
    if z < 0.78:
        z -= 0.00344129
    else:
        z = 0.77655871 + (z - 0.78) * 1.019
    return Vector((x, y, z))


def prepare_rig():
    reference = imported(PACKAGE/'Source/arin-v5.7-rig-reference.fbx')
    rig = next(obj for obj in reference if obj.type == 'ARMATURE')
    action_for(rig, None)
    normalize(rig, None)
    rig.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    # Build the donor surface in the fitted rest space. Barycentric transfer
    # supports different topology without pretending vertex indices match.
    points, triangles, weights = [], [], []
    for obj in reference:
        if obj.type != 'MESH':
            continue
        offset = len(points)
        points.extend(fit_point(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices)
        weights.extend({obj.vertex_groups[g.group].name: g.weight for g in v.groups}
                       for v in obj.data.vertices)
        obj.data.calc_loop_triangles()
        triangles.extend(tuple(offset + index for index in tri.vertices)
                         for tri in obj.data.loop_triangles)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in rig.data.edit_bones:
        old_direction = bone.tail - bone.head
        old_head = bone.head.copy()
        bone.use_connect = False
        bone.head = fit_point(old_head)
        # Preserve each reference rest basis for the original local rotations.
        bone.tail = bone.head + old_direction * (fit_point(old_head + old_direction)
                                                - fit_point(old_head)).length / old_direction.length
    # v5.8 has open five-finger hands, unlike the old clenched, single-finger
    # donor. Fit its arm joints and build independent finger chains from this
    # mesh's landmarks. Never use the old finger weights or local rotations.
    for bone in list(rig.data.edit_bones):
        if 'HandIndex' in bone.name:
            rig.data.edit_bones.remove(bone)
    for side, sign in [('Left', 1), ('Right', -1)]:
        points_by_bone = {
            'Shoulder': ((.04, .033, .823), (.145, .035, .796)),
            'Arm': ((.145, .035, .796), (.270, .035, .791)),
            'ForeArm': ((.270, .035, .791), (.402, .028, .784)),
            'Hand': ((.402, .028, .784), (.445, .024, .783)),
        }
        for suffix, (head, tail) in points_by_bone.items():
            bone = rig.data.edit_bones['mixamorig:' + side + suffix]
            bone.head = Vector((head[0]*sign, head[1], head[2]))
            bone.tail = Vector((tail[0]*sign, tail[1], tail[2]))
            bone.align_roll(Vector((0, 0, 1)))
        fingers = [('Pinky', .048, .442, .477), ('Ring', .033, .447, .489),
                   ('Middle', .017, .449, .497), ('Index', .001, .445, .489),
                   ('Thumb', -.010, .416, .455)]
        for finger, y, start, end in fingers:
            parent = rig.data.edit_bones['mixamorig:' + side + 'Hand']
            for index in range(3):
                bone = rig.data.edit_bones.new(f'{side}{finger}{index+1}')
                bone.head = (sign*(start+(end-start)*index/3), y, .781)
                bone.tail = (sign*(start+(end-start)*(index+1)/3), y, .781)
                bone.parent = parent
                bone.align_roll(Vector((0, 0, 1)))
                parent = bone
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in reference:
        if obj != rig:
            bpy.data.objects.remove(obj, do_unlink=True)
    rig.name = 'Arin v5.8 Candidate Rig'
    return rig, points, triangles, weights


def bind_body(rig, points, triangles, weights):
    body = [obj for obj in imported(PACKAGE/'Source/arin-v5.8.original.glb')
            if obj.type == 'MESH']
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True)
    distances = []
    for obj in body:
        if obj.type != 'MESH':
            continue
        obj.name = 'ArinV58.' + obj.name
        transform = obj.matrix_world.copy()
        obj.data.transform(transform)
        obj.parent = rig
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = Matrix.Identity(4)
        groups = {b.name: obj.vertex_groups.new(name=b.name) for b in rig.data.bones}
        for vertex in obj.data.vertices:
            nearest, _, face, distance = tree.find_nearest(vertex.co)
            distances.append(distance)
            a, b, c = triangles[face]
            bary = barycentric_transform(nearest, points[a], points[b], points[c],
                                         Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
            merged = {}
            for donor, factor in zip((a, b, c), bary):
                for name, weight in weights[donor].items():
                    if name in groups:
                        merged[name] = merged.get(name, 0.0) + weight * max(0.0, factor)
            x, y, z = vertex.co
            if z > .715 and abs(x) > .13:
                # Anatomical weights for the new arms prevent cross-transfer
                # from the old gauntlet/fist and preserve separate armor forms.
                side = 'Left' if x > 0 else 'Right'
                position = abs(x)
                if position < .25:
                    mix = max(0.0, min(1.0, (position-.14)/.035))
                    merged = {'mixamorig:'+side+'Shoulder': 1-mix,
                              'mixamorig:'+side+'Arm': mix}
                elif position < .30:
                    mix = max(0.0, min(1.0, (position-.252)/.03))
                    merged = {'mixamorig:'+side+'Arm': 1-mix,
                              'mixamorig:'+side+'ForeArm': mix}
                else:
                    mix = max(0.0, min(1.0, (position-.390)/.027))
                    merged = {'mixamorig:'+side+'ForeArm': 1-mix,
                              'mixamorig:'+side+'Hand': mix}
            strongest = sorted(merged.items(), key=lambda item: item[1], reverse=True)[:4]
            total = sum(weight for _, weight in strongest)
            if total <= 0:
                raise RuntimeError('Unweighted candidate vertex')
            for name, weight in strongest:
                groups[name].add([vertex.index], weight / total, 'REPLACE')
        obj.modifiers.new('Candidate Skin', 'ARMATURE').object = rig
    # Heat-weight the continuous new hand meshes against their own five-finger
    # chains. Spatial classification alone is discontinuous at the thumb web.
    for part, side in [('tripo_part_2', 'Left'), ('tripo_part_3', 'Right')]:
        hand = next(obj for obj in body if obj.name == 'ArinV58.' + part)
        for bone in rig.data.bones:
            bone.use_deform = bone.name.startswith(side) or bone.name in (
                'mixamorig:'+side+'Hand', 'mixamorig:'+side+'ForeArm')
        temporary = hand.copy()
        temporary.data = hand.data.copy()
        bpy.context.collection.objects.link(temporary)
        temporary.vertex_groups.clear()
        temporary.modifiers.clear()
        topology = bmesh.new()
        topology.from_mesh(temporary.data)
        bmesh.ops.remove_doubles(topology, verts=list(topology.verts), dist=.00001)
        topology.to_mesh(temporary.data)
        topology.free()
        bpy.ops.object.select_all(action='DESELECT')
        temporary.select_set(True)
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        if any(not vertex.groups for vertex in temporary.data.vertices):
            raise RuntimeError('Automatic new-hand weighting left unweighted vertices')
        lookup = KDTree(len(temporary.data.vertices))
        for vertex in temporary.data.vertices:
            lookup.insert(vertex.co, vertex.index)
        lookup.balance()
        hand.vertex_groups.clear()
        target_groups = [hand.vertex_groups.new(name=group.name)
                         for group in temporary.vertex_groups]
        for vertex in hand.data.vertices:
            _, index, distance = lookup.find(vertex.co)
            if distance > .00002:
                raise RuntimeError('Temporary hand weld changed source correspondence')
            for group in temporary.data.vertices[index].groups:
                target_groups[group.group].add([vertex.index], group.weight, 'REPLACE')
        temporary_mesh = temporary.data
        bpy.data.objects.remove(temporary, do_unlink=True)
        bpy.data.meshes.remove(temporary_mesh)
    for bone in rig.data.bones:
        bone.use_deform = True
    distances.sort()
    return body, {'method': 'Body: fitted donor surface; arms: new anatomical weights; hands: welded-proxy heat weights',
                  'maximumDistance': max(distances),
                  'medianDistance': distances[len(distances)//2],
                  'percentile95Distance': distances[int(len(distances)*0.95)],
                  'unweightedVertices': 0, 'artistDeformationApproval': 'Pending'}


def load_motion(rig, path, action_name, finger_pose=None):
    objects = imported(path)
    donor = next(obj for obj in objects if obj.type == 'ARMATURE')
    source_action = donor.animation_data.action
    normalize(donor, source_action)
    action = bpy.data.actions.new(action_name)
    action_for(rig, action)
    rig.data.pose_position = 'POSE'
    for bone in rig.pose.bones:
        bone.rotation_mode = 'QUATERNION'
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start, scene.frame_end = map(round, source_action.frame_range)
    mapped = [bone for bone in rig.pose.bones if bone.name in donor.pose.bones]
    for frame in range(scene.frame_start, scene.frame_end+1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        desired = {}
        for bone in mapped:
            source = donor.pose.bones[bone.name]
            # Retarget in armature space; differing hand/forearm rest axes
            # cannot safely share raw local quaternion channels.
            delta = source.matrix.to_quaternion() @ source.bone.matrix_local.to_quaternion().inverted()
            desired[bone.name] = delta @ bone.bone.matrix_local.to_quaternion()
        for bone in mapped:
            rest = bone.bone.matrix_local
            local_rest = bone.parent.bone.matrix_local.inverted() @ rest if bone.parent else rest
            parent_rotation = desired[bone.parent.name] if bone.parent else Quaternion()
            bone.rotation_quaternion = local_rest.to_quaternion().inverted() @ parent_rotation.inverted() @ desired[bone.name]
            bone.location = donor.pose.bones[bone.name].location if bone.parent is None else (0, 0, 0)
            bone.keyframe_insert('rotation_quaternion', frame=frame)
            bone.keyframe_insert('location', frame=frame)
        for bone in rig.pose.bones:
            if bone.name in desired:
                continue
            if finger_pose and bone.name in finger_pose:
                bone.rotation_quaternion = finger_pose[bone.name]
            else:
                # A new, editable v5.8 grip; none of the old fist curves are used.
                angles = (35, 45, 25) if 'Thumb' in bone.name else (55, 70, 45)
                bone.rotation_quaternion = Quaternion((1, 0, 0), -math.radians(angles[int(bone.name[-1])-1]))
            bone.keyframe_insert('rotation_quaternion', frame=frame)
    action.use_fake_user = True
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    scene.frame_set(scene.frame_start)
    bpy.context.view_layer.update()
    return action


def load_idle(rig):
    return load_motion(rig, PACKAGE/'Source/arin-v5.7-idle-motion.fbx', 'Idle')


def fit_equipment(rig):
    objects = imported(PACKAGE/'Source/arin-v5.7-equipment-source.glb')
    use_new_sword = '--old-sword' not in sys.argv
    if use_new_sword:
        objects.extend(imported(PACKAGE/'Equipment/arin-v5.8-sword.cleaned.glb'))
    props = []
    for source_name, bone_name, output_name in [
        ('ArinV58_Sword' if use_new_sword else 'Sword', 'mixamorig:RightHand', 'Sword — Adjust This'),
        ('Shield', 'mixamorig:LeftHand', 'Shield — Adjust This')
    ]:
        obj = next(o for o in objects if o.name == source_name and o.type == 'MESH')
        # Bake only the original equipment geometry; no saved or builder offsets.
        obj.data.transform(obj.matrix_world)
        obj.parent = None
        obj.matrix_world = Matrix.Identity(4)
        obj.modifiers.clear()
        obj.vertex_groups.clear()
        if source_name == 'Sword':
            repair, before = straighten_sword(obj)
            (PACKAGE/'Diagnostics/sword-grip-repair.json').write_text(json.dumps(repair, indent=2))
            (PACKAGE/'Diagnostics/sword-before-vertices.json').write_text(json.dumps(before))
        elif source_name == 'ArinV58_Sword':
            source_height = max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
            obj.data.transform(Matrix.Scale(.60/source_height, 4)
                               @ Matrix.Rotation(math.pi, 4, 'Y')
                               @ Matrix.Translation((-.000122, .000175, -.865)))
        points = [v.co.copy() for v in obj.data.vertices]
        lo = Vector([min(v[i] for v in points) for i in range(3)])
        hi = Vector([max(v[i] for v in points) for i in range(3)])
        center = (lo + hi) * 0.5
        # Keep source dimensions and put the prop's origin at its grip. Sin
        # approves rotation/position in this Idle scene before propagation.
        grip = center.copy()
        if source_name in ('Sword', 'ArinV58_Sword'):
            grip = Vector()
            rotation = Matrix.Identity(4)
        else:
            rotation = Matrix.Identity(4)
        obj.data.transform(rotation @ Matrix.Translation(-grip))
        hand = rig.matrix_world @ rig.pose.bones[bone_name].matrix
        sign = -1 if 'Right' in bone_name else 1
        grip_in_rest = Vector((sign*.448, .022, .767))
        target = hand @ rig.data.bones[bone_name].matrix_local.inverted() @ grip_in_rest
        if source_name == 'Shield':
            target.y -= .018
        obj.parent = rig
        obj.parent_type = 'BONE'
        obj.parent_bone = bone_name
        bpy.context.view_layer.update()
        obj.matrix_world = Matrix.Translation(target)
        obj.name = output_name
        obj['Source'] = ('Arin v5.8 cleaned new sword' if source_name == 'ArinV58_Sword'
                         else 'Arin v5.7 original equipment geometry')
        obj['Grip Status'] = 'Provisional — Sin to adjust in Idle'
        props.append(obj)
    for obj in objects:
        if obj not in props:
            bpy.data.objects.remove(obj, do_unlink=True)
    return props


def minimum(body):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    low = float('inf')
    for obj in body:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        low = min(low, min((evaluated.matrix_world @ v.co).z for v in mesh.vertices))
        evaluated.to_mesh_clear()
    return low


def presentation(rig, props):
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('Arin Review World')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.11, 0.11, 0.11, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.7
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    target = Vector((0, 0, 0.53))
    bpy.ops.object.camera_add(location=(0.25, -2.7, 1.0))
    camera = bpy.context.object
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 1.35
    scene.camera = camera
    for name, location, power in [('Key', (-2, -3, 4), 350), ('Fill', (3, -1, 2), 200)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = power
        light.data.size = 3
        light.rotation_euler = (target-light.location).to_track_quat('-Z', 'Y').to_euler()
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            space.shading.type = 'MATERIAL'
            space.overlay.show_extras = False
            space.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
            space.region_3d.view_distance = 1.8
            space.region_3d.view_location = target
            space.region_3d.view_perspective = 'ORTHO'
    rig.show_in_front = True
    rig.hide_set(True)
    bpy.ops.object.select_all(action='DESELECT')
    props[0].select_set(True)
    bpy.context.view_layer.objects.active = props[0]
    scene['Candidate'] = 'Arin v5.8 — provisional local rig and Idle equipment review'
    scene['Calibration'] = 'No v5.7 Studio calibrations imported'
    bpy.ops.file.pack_all()
    scene.render.filepath = str(PACKAGE/'Previews/Idle.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-idle-review.blend'))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig, points, triangles, weights = prepare_rig()
    body, transfer = bind_body(rig, points, triangles, weights)
    bind_minimum = minimum(body)
    action = load_idle(rig)
    props = fit_equipment(rig)
    idle_minimum = minimum(body)
    # One new-package standing baseline, measured from the body, not v5.7 values.
    rig.location.z -= idle_minimum
    bpy.context.view_layer.update()
    report = {'version': '5.8-candidate', 'sourceCalibrationApplied': False,
              'bodyTriangles': sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in body),
              'rigBones': len(rig.data.bones), 'skinTransfer': transfer,
              'bindBodyMinimumZ': bind_minimum, 'idleBodyMinimumZBeforePlacement': idle_minimum,
              'standingOffsetZ': rig.location.z, 'idleBodyMinimumZ': minimum(body),
              'idleFrameRange': list(action.frame_range), 'otherAnimations': 'Pending approved Idle grip',
              'equipment': [o.name for o in props]}
    (PACKAGE/'Diagnostics/idle-preparation.json').write_text(json.dumps(report, indent=2))
    presentation(rig, props)
    print('ARIN_V58_CANDIDATE=' + json.dumps(report))


if __name__ == '__main__':
    main()

"""Bake unique finishes and export the Studio cutaway from the editable shop."""
import hashlib
import json
import math
import struct
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
if not bpy.app.background:
    raise RuntimeError('Run in background Blender; never modify the live review scene.')
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'Neris-Weapon-Shop-V2.blend'))
scene = bpy.context.scene
bpy.context.window.view_layer = scene.view_layers['Interior - roof and entrance removed']
layer = bpy.context.view_layer
# Keep fine trim inexpensive in the game; the editable master stays untouched.
for obj in layer.objects:
    for modifier in obj.modifiers:
        if modifier.type == 'BEVEL':
            modifier.segments = 1
    if obj.type in {'CURVE', 'FONT'}:
        obj.data.bevel_resolution = 0 if obj.data.bevel_depth <= .05 else 1
        if obj.type == 'FONT':
            obj.data.resolution_u = 4
            obj.data.extrude = 0
            obj.data.bevel_depth = 0
        else:
            for spline in list(obj.data.splines):
                if spline.type == 'POLY' and spline.use_cyclic_u and len(spline.points) > 64:
                    points = [tuple(point.co) for point in spline.points][::2]
                    obj.data.splines.remove(spline)
                    reduced = obj.data.splines.new('POLY')
                    reduced.points.add(len(points)-1)
                    for point, co in zip(reduced.points, points):
                        point.co = co
                    reduced.use_cyclic_u = True
layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
source = [o for o in layer.objects if o.type in {'MESH', 'CURVE', 'FONT'} and o.visible_get()]
groups = {}
for obj in source:
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph), depsgraph=depsgraph)
    mesh.transform(obj.matrix_world)
    duplicate = bpy.data.objects.new(obj.name + ' runtime', mesh)
    scene.collection.objects.link(duplicate)
    material = mesh.materials[0]
    assert len(mesh.materials) == 1, obj.name
    groups.setdefault(material.name, []).append(duplicate)
for obj in list(scene.objects):
    if not obj.name.endswith(' runtime'):
        bpy.data.objects.remove(obj, do_unlink=True)

# Bound each primitive below the native 100,000-vertex accessor limit even
# when every triangle corner needs a separate UV/normal vertex.
chunks = {}
for name, objects in groups.items():
    batch, triangles, ordinal = [], 0, 1
    for obj in objects:
        count = sum(len(face.vertices)-2 for face in obj.data.polygons)
        assert count <= 28000, obj.name
        if triangles + count > 28000:
            chunks[f'{name} {ordinal}'] = batch
            batch, triangles, ordinal = [], 0, ordinal + 1
        batch.append(obj)
        triangles += count
    chunks[f'{name} {ordinal}'] = batch

try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type != 'CPU'
    if any(d.use for d in prefs.devices):
        scene.cycles.device = 'GPU'
except Exception:
    scene.cycles.device = 'CPU'
scene.cycles.samples = 1
parts = []
for part_name, objects in chunks.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = 'Neris armory - ' + part_name
    mesh = obj.data
    material = mesh.materials[0]
    name = material.name
    mesh.materials.clear()
    mesh.materials.append(material)
    for face in mesh.polygons:
        face.material_index = 0
    for uv in list(mesh.uv_layers):
        mesh.uv_layers.remove(uv)
    shader = material.node_tree.nodes.get('Principled BSDF')
    links = material.node_tree.links
    color = shader.inputs['Base Color']
    if color.is_linked:
        # Every island is unique in this atlas. No UV or image is repeated.
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin=.008)
        bpy.ops.object.mode_set(mode='OBJECT')
        size = 2048 if name in {'Floor', 'Ivory'} else 1024
        image = bpy.data.images.new('Neris unique ' + name, width=size, height=size)
        nodes = material.node_tree.nodes
        texture = nodes.new('ShaderNodeTexImage')
        texture.image = image
        nodes.active = texture
        output = nodes.get('Material Output')
        emission = nodes.new('ShaderNodeEmission')
        links.new(color.links[0].from_socket, emission.inputs['Color'])
        links.new(emission.outputs[0], output.inputs['Surface'])
        scene.render.bake.margin = 8
        bpy.ops.object.bake(type='EMIT')
        links.new(shader.outputs[0], output.inputs['Surface'])
        links.new(texture.outputs['Color'], color)
        nodes.remove(emission)
        image.pack()
        # The native material uses the actual modeled bevels for its small detail.
        for link in list(shader.inputs['Normal'].links):
            links.remove(link)
    else:
        uv = mesh.uv_layers.new(name='UVMap')
        for face in mesh.polygons:
            dominant = max(range(3), key=lambda axis: abs(face.normal[axis]))
            axes = [axis for axis in range(3) if axis != dominant]
            for index in face.loop_indices:
                co = mesh.vertices[mesh.loops[index].vertex_index].co
                uv.data[index].uv = (co[axes[0]], co[axes[1]])
    # The continuous floor top is the same Y=0 grounding plane used by party actors.
    for vertex in mesh.vertices:
        vertex.co.z -= .035
    parts.append(obj)
    print('Prepared', name, len(mesh.polygons), flush=True)

bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.triangulate(mesh, faces=list(mesh.faces))
    # Font bevels can collapse at sharp glyph corners; they own no visible area.
    collapsed = [face for face in mesh.faces if face.calc_area() < 1e-12]
    if collapsed:
        print('Removed collapsed faces', obj.name, len(collapsed), flush=True)
        bmesh.ops.delete(mesh, geom=collapsed, context='FACES_ONLY')
    mesh.to_mesh(obj.data)
    mesh.free()
assert 0 < len(parts) <= 16
bpy.ops.export_scene.gltf(filepath=str(ROOT / 'Armory-Room.glb'), export_format='GLB',
                          use_selection=True, export_animations=False, export_tangents=True)

# Sharp beveled lettering occasionally yields a zero Mikk tangent. These
# isotropic materials have no normal maps, so any orthogonal basis is valid.
# Preserve valid exported tangents and repair only unusable corners.
path = ROOT / 'Armory-Room.glb'
payload = bytearray(path.read_bytes())
json_size = struct.unpack_from('<I', payload, 12)[0]
document = json.loads(payload[20:20+json_size])
vertex_counts = [document['accessors'][p['attributes']['POSITION']]['count']
                 for mesh in document['meshes'] for p in mesh['primitives']]
print('Runtime vertex counts', vertex_counts, 'total', sum(vertex_counts), flush=True)
assert max(vertex_counts) <= 100000 and sum(vertex_counts) <= 131072
binary_start = 28 + json_size
repaired = 0
def attribute_offset(accessor_index, index, components):
    accessor = document['accessors'][accessor_index]
    view = document['bufferViews'][accessor['bufferView']]
    assert accessor['componentType'] == 5126
    return binary_start + view.get('byteOffset', 0) + accessor.get('byteOffset', 0) + index * view.get('byteStride', components * 4)
for mesh in document['meshes']:
    for primitive in mesh['primitives']:
        assert 'normalTexture' not in document['materials'][primitive['material']]
        attributes = primitive['attributes']
        tangent_accessor = attributes['TANGENT']
        for index in range(document['accessors'][tangent_accessor]['count']):
            offset = attribute_offset(tangent_accessor, index, 4)
            normal = Vector(struct.unpack_from('<3f', payload, attribute_offset(attributes['NORMAL'], index, 3)))
            normal.normalize()
            tangent = Vector(struct.unpack_from('<3f', payload, offset))
            orthogonal = tangent - normal * normal.dot(tangent)
            if not math.isfinite(orthogonal.length_squared) or orthogonal.length_squared < 1e-12:
                axis = Vector((1, 0, 0)) if abs(normal.x) < .8 else Vector((0, 1, 0))
                tangent = normal.cross(axis).normalized()
                struct.pack_into('<4f', payload, offset, *tangent, 1)
                repaired += 1
path.write_bytes(payload)
print('Repaired unusable untextured normal bases', repaired, flush=True)
(ROOT / 'room.sm3d.json').write_text('{"version":1}\n')
report = {
    'parts': len(parts),
    'triangles': sum(len(p.vertices)-2 for o in parts for p in o.data.polygons),
    'uniqueBakedImages': len([i for i in bpy.data.images if i.name.startswith('Neris unique')]),
    'nativeScalePercent': 1000,
    'repairedTangentCorners': repaired,
    'vertices': sum(vertex_counts),
    'source': 'Neris-Weapon-Shop-V2.blend',
    'sha256': hashlib.sha256((ROOT / 'Armory-Room.glb').read_bytes()).hexdigest(),
}
(ROOT / 'runtime-report.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report), flush=True)

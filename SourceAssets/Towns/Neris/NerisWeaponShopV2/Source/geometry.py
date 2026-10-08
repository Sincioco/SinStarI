"""Editable mesh helpers and the Neris ivory / teal / brass material palette."""
import math
import bpy
from mathutils import Vector

MATERIALS = {}
ACTIVE = None


def collection(name):
    global ACTIVE
    ACTIVE = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(ACTIVE)
    return ACTIVE


def finish(obj, name, material):
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    ACTIVE.objects.link(obj)
    if material:
        obj.data.materials.append(MATERIALS[material])
    return obj


def palette():
    specs = [
        ('Ivory', (.70, .64, .48), 0, .67),
        ('WarmStone', (.43, .36, .25), 0, .72),
        ('Floor', (.115, .17, .175), .15, .34),
        ('Teal', (.016, .145, .16), .25, .29),
        ('DeepTeal', (.008, .042, .054), .1, .48),
        ('Gold', (.62, .36, .105), .78, .25),
        ('Steel', (.42, .56, .63), .88, .22),
        ('Iron', (.027, .039, .045), .8, .36),
        ('Walnut', (.115, .055, .025), 0, .46),
        ('Leather', (.13, .054, .029), 0, .73),
        ('Linen', (.56, .44, .29), 0, .85),
        ('Crystal', (.035, .57, .70), .18, .19),
        ('Glow', (.36, .85, .94), .0, .25),
        ('Amber', (1., .42, .075), .0, .25),
    ]
    for name, color, metallic, roughness in specs:
        material = bpy.data.materials.new(name)
        material.diffuse_color = (*color, 1)
        material.use_nodes = True
        nodes, links = material.node_tree.nodes, material.node_tree.links
        shader = nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (*color, 1)
        shader.inputs['Metallic'].default_value = metallic
        shader.inputs['Roughness'].default_value = roughness
        if name in ('Glow', 'Amber', 'Crystal'):
            shader.inputs['Emission Color'].default_value = (*color, 1)
            shader.inputs['Emission Strength'].default_value = 3 if name != 'Crystal' else .45
        # Global position makes every surface unique; no UV tiles or repeated images.
        if name in ('Ivory', 'WarmStone', 'Floor', 'Walnut', 'Leather'):
            position = nodes.new('ShaderNodeNewGeometry')
            scale = nodes.new('ShaderNodeVectorMath')
            scale.operation = 'MULTIPLY'
            scale.inputs[1].default_value = (3, 35, 3) if name == 'Walnut' else (1, 1, 1)
            links.new(position.outputs['Position'], scale.inputs[0])
            noise = nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 3.5 if name == 'Floor' else 8
            noise.inputs['Detail'].default_value = 3
            links.new(scale.outputs['Vector'], noise.inputs['Vector'])
            ramp = nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].color = (*(v * .78 for v in color), 1)
            ramp.color_ramp.elements[1].color = (*(min(1, v * 1.14) for v in color), 1)
            links.new(noise.outputs['Fac'], ramp.inputs[0])
            links.new(ramp.outputs[0], shader.inputs['Base Color'])
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = .16
            bump.inputs['Distance'].default_value = .018 if name != 'Floor' else .007
            links.new(noise.outputs['Fac'], bump.inputs['Height'])
            links.new(bump.outputs[0], shader.inputs['Normal'])
        MATERIALS[name] = material


def box(name, center, size, material, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        edge = obj.modifiers.new('Crafted edge', 'BEVEL')
        edge.width, edge.segments = bevel, 3
        obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return finish(obj, name, material)


def cylinder(name, center, radius, depth, material, vertices=48, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                      location=center)
    obj = finish(bpy.context.object, name, material)
    if rotation:
        obj.rotation_euler = rotation
    edge = obj.modifiers.new('Machined edge', 'BEVEL')
    edge.width, edge.segments = min(.025, depth / 6), 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj


def mesh(name, vertices, faces, material):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    ACTIVE.objects.link(obj)
    data.materials.append(MATERIALS[material])
    return obj


def path(name, points, radius, material, closed=False):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth, data.bevel_resolution = radius, 3
    line = data.splines.new('POLY')
    line.points.add(len(points) - 1)
    for vertex, point in zip(line.points, points):
        vertex.co = (*point, 1)
    line.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, data)
    ACTIVE.objects.link(obj)
    data.materials.append(MATERIALS[material])
    return obj


def rod(name, a, b, radius, material):
    obj = cylinder(name, (Vector(a) + Vector(b)) / 2, radius,
                   (Vector(b) - Vector(a)).length, material, 12)
    obj.rotation_euler = (Vector(b) - Vector(a)).to_track_quat('Z', 'Y').to_euler()
    return obj


def text(name, words, location, size, material='Gold'):
    data = bpy.data.curves.new(name, 'FONT')
    data.body, data.size = words, size
    data.align_x, data.align_y = 'CENTER', 'CENTER'
    data.extrude, data.bevel_depth = .004, .002
    obj = bpy.data.objects.new(name, data)
    ACTIVE.objects.link(obj)
    obj.location, obj.rotation_euler = location, (math.pi / 2, 0, 0)
    data.materials.append(MATERIALS[material])
    return obj


def star(name, center, radius, material='Gold', rotation=0):
    x, y, z = center
    points = [(x, y, z)]
    for i in range(16):
        angle = i * math.pi / 8 + rotation
        r = radius * (1 if i % 4 == 0 else .68 if i % 2 == 0 else .22)
        points.append((x + r * math.sin(angle), y, z + r * math.cos(angle)))
    return mesh(name, points, [(0, i + 1, (i + 1) % 16 + 1) for i in range(16)], material)

"""Remove generated blade protrusions and make a 5K–10K-triangle sword copy."""
import bpy
import bmesh
import hashlib
import json
import struct
from pathlib import Path
from mathutils import Vector

PACKAGE = Path(__file__).resolve().parents[1]
SOURCE = PACKAGE/'Source/arin-v5.8-new-sword.original.glb'
OUTPUT = PACKAGE/'Equipment/arin-v5.8-sword.cleaned.glb'


def active(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))
    sword = next(obj for obj in bpy.data.objects if obj.type == 'MESH')
    world = sword.matrix_world.copy()
    sword.parent = None
    sword.matrix_world = world
    active(sword)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    initial_triangles = len(sword.data.polygons)
    mesh = bmesh.new()
    mesh.from_mesh(sword.data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=.00000001)
    source_boundaries = sum(edge.is_boundary for edge in mesh.edges)
    source_nonmanifold = sum(len(edge.link_faces) > 2 for edge in mesh.edges)
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    mesh.to_mesh(sword.data)
    mesh.free()
    # Preserve original per-corner UVs while collapsing redundant generated
    # geometry. Use a small reserve for the five protrusion cuts and caps.
    modifier = sword.modifiers.new('Reduce For Character Inspection', 'DECIMATE')
    modifier.ratio = 8500/initial_triangles
    modifier.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    print('SWORD_REDUCTION_COMPLETE', flush=True)
    # The inspection establishes a regular side profile below the ornate
    # collar. Boolean cuts close their surfaces; deleting faces would leave holes.
    for sign in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, sign*.5137, -.19))
        cutter = bpy.context.object
        cutter.name = 'Temporary Blade Protrusion Cutter'
        cutter.dimensions = (1, 1, 1.62)  # top Z=.62; near Y=+/-.0137
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        active(sword)
        modifier = sword.modifiers.new('Remove Side Protrusions', 'BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.solver = 'EXACT'
        modifier.use_self = False
        modifier.object = cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
    # The generator's intersecting surfaces can leave a few tiny residual
    # vertices at the collar. Flatten only these onto the same cut side plane;
    # global self-intersection repair would unnecessarily alter the ornate hilt.
    flattened_residuals = 0
    for vertex in sword.data.vertices:
        if vertex.co.z < .6199 and abs(vertex.co.y) > .0137:
            vertex.co.y = .0137 if vertex.co.y > 0 else -.0137
            flattened_residuals += 1
    mesh = bmesh.new()
    mesh.from_mesh(sword.data)
    bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=.00000001)
    blade_edges = [edge for edge in mesh.edges if all(v.co.z < .62 for v in edge.verts)]
    bmesh.ops.dissolve_degenerate(mesh, edges=blade_edges, dist=.0000001)
    cut_boundaries = [edge for edge in mesh.edges if edge.is_boundary
                     and all(v.co.z < .62 for v in edge.verts)]
    capped_faces = 0
    if cut_boundaries:
        capped_faces = len(bmesh.ops.holes_fill(mesh, edges=cut_boundaries, sides=0)['faces'])
    bmesh.ops.recalc_face_normals(mesh, faces=list(mesh.faces))
    bmesh.ops.triangulate(mesh, faces=list(mesh.faces))
    boundary_edges = sum(edge.is_boundary for edge in mesh.edges)
    blade_boundaries = sum(edge.is_boundary and all(v.co.z < .62 for v in edge.verts)
                           for edge in mesh.edges)
    mesh.to_mesh(sword.data)
    mesh.free()
    sword.name = 'ArinV58_Sword'
    count = len(sword.data.polygons)
    protrusions = [v.index for v in sword.data.vertices
                   if v.co.z < .6199 and abs(v.co.y) > .013701]
    if protrusions:
        details = [list(sword.data.vertices[i].co) for i in protrusions[:10]]
        raise RuntimeError(f'{len(protrusions)} vertices remain outside the blade profile: {details}')
    if not 5000 <= count <= 10000:
        raise RuntimeError(f'Sword triangle count is outside requested range: {count}')
    if blade_boundaries or boundary_edges > source_boundaries:
        raise RuntimeError(f'Cleanup introduced open edges: blade={blade_boundaries}, '
                           f'total={boundary_edges}, original={source_boundaries}')
    OUTPUT.parent.mkdir(exist_ok=True)
    active(sword)
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT), export_format='GLB',
                              use_selection=True, export_animations=False,
                              export_materials='EXPORT')
    exported = OUTPUT.read_bytes()
    json_length = struct.unpack_from('<I', exported, 12)[0]
    gltf = json.loads(exported[20:20+json_length])
    exported_count = sum(gltf['accessors'][p['indices']]['count']//3
                         for m in gltf['meshes'] for p in m['primitives'])
    if not 5000 <= exported_count <= 10000:
        raise RuntimeError(f'Exported sword exceeds requested range: {exported_count}')
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('Sword Review World')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.18,.18,.18,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .8
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 16
    scene.render.resolution_x = 800
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    target = Vector((0,0,.49))
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 1.06
    scene.camera = camera
    for location, power in [((-2,-3,3),350), ((3,2,1),200)]:
        bpy.ops.object.light_add(type='AREA', location=location)
        light = bpy.context.object
        light.data.energy = power
        light.data.size = 3
        light.rotation_euler = (target-light.location).to_track_quat('-Z','Y').to_euler()
    for name, direction in [('Front', (0,-2,0)), ('Side', (2,0,0))]:
        camera.location = target+Vector(direction)
        camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath = str(PACKAGE/f'Previews/New-Sword-{name}.png')
        bpy.ops.render.render(write_still=True)
    active(sword)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-sword-cleaned.blend'), compress=True)
    report = {'source':SOURCE.name, 'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'originalTriangles':initial_triangles, 'cleanedTriangles':count,
              'exportedTriangles':exported_count,
              'reductionPercent':100*(1-count/initial_triangles),
              'openBoundaryEdges':boundary_edges, 'remainingSideProtrusionVertices':len(protrusions),
              'bladeOpenBoundaryEdges':blade_boundaries,
              'originalHiltBoundaryEdges':source_boundaries,
              'originalNonManifoldEdges':source_nonmanifold,
              'smallCutHolesCapped':capped_faces,
              'residualBladeVerticesFlattened':flattened_residuals,
              'bladeSideLimit':.0137, 'collarStartZ':.62,
              'outputSha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              'materials':'Original base color, normal, and metallic/roughness textures retained'}
    (PACKAGE/'Diagnostics/new-sword-cleanup.json').write_text(json.dumps(report,indent=2))
    print('SWORD_CLEANUP='+json.dumps(report), flush=True)


if __name__ == '__main__':
    main()

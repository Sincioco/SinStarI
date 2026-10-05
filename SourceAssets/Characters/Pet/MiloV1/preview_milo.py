"""Render a reproducible contact sheet from the exported GLB, not just the rig."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps = 30
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'milo-v1-animated.glb'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
body = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
actions = {a.name: a for a in bpy.data.actions}
assert set(actions) == {'Idle','Walk','Run','Attack','Defend','Hit','Death','Victory'}, list(actions)
scene = bpy.context.scene
scene.render.fps = 30
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1800
scene.render.resolution_y = 1500
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new('PreviewWorld')
scene.world.color = (.2,.2,.2)
scene.view_settings.view_transform = 'AgX'
report = {}
for index, (name, frame) in enumerate([('Idle',0),('Walk',8),('Run',6),('Attack',17),
                                      ('Defend',30),('Hit',5),('Death',66),('Victory',38)]):
    rig.animation_data.action = actions[name]
    rig.animation_data.action_slot = actions[name].slots[0]
    samples = []
    first_points = None
    for f in range(int(round(actions[name].frame_range[1]))+1):
        scene.frame_set(f)
        depsgraph=bpy.context.evaluated_depsgraph_get()
        evaluated = body.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        pts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        if first_points is None:
            first_points = pts
        low = min(p.z for p in pts)
        assert low > -.002, (name, f, low)
        samples.append(round(low,7))
        evaluated.to_mesh_clear()
    report[name] = {'frameZeroMinimumY':samples[0], 'minimumY':min(samples),
                    'maximumContactY':max(samples),'finalMinimumY':samples[-1]}
    if name in ['Idle', 'Walk', 'Run']:
        seam = max((a-b).length for a,b in zip(first_points, pts))
        report[name]['maximumLoopSeamMeters'] = seam
        assert seam < .002, ('Loop seam', name, seam)
    scene.frame_set(frame)
    mesh=bpy.data.meshes.new_from_object(body.evaluated_get(depsgraph),depsgraph=depsgraph)
    copy=bpy.data.objects.new(name,mesh)
    scene.collection.objects.link(copy)
    # Present each exported sample at the same scale, in three-quarter view.
    copy.rotation_euler.z = -.48
    copy.location = ((index%4-1.5)*1.25, 0, (1-index//4)*1.35)
    bpy.ops.object.text_add(location=(copy.location.x-.5,-.63,copy.location.z-.16))
    label=bpy.context.object
    label.data.body=name+'  /  '+str(frame)
    label.data.size=.105
    label.rotation_euler=(math.pi/2,0,0)
    bpy.ops.mesh.primitive_plane_add(size=1.0,location=(copy.location.x,0,copy.location.z-.008))
    plane=bpy.context.object
    plane.scale=(1.15,1.12,1)
    mat=bpy.data.materials.get('Floor') or bpy.data.materials.new('Floor')
    mat.diffuse_color=(.10,.14,.19,1)
    plane.data.materials.append(mat)
body.hide_render=True
rig.hide_render=True
bpy.ops.object.camera_add(location=(0,-8,3.05))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,1.1))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'
camera.data.ortho_scale=5.25
scene.camera=camera
for position,energy,size in [((0,-4,5),1000,6),((3,1,4),800,5)]:
    bpy.ops.object.light_add(type='AREA',location=position)
    light=bpy.context.object
    light.data.energy=energy
    light.data.shape='DISK'
    light.data.size=size
    light.rotation_euler=(Vector((0,0,1))-light.location).to_track_quat('-Z','Y').to_euler()
(ROOT/'Previews').mkdir(exist_ok=True)
scene.render.filepath=str(ROOT/'Previews'/'animation-contact-sheet.png')
bpy.ops.render.render(write_still=True)
(ROOT/'export-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('MILO GLB ROUNDTRIP PASS',report)

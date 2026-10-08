"""Inspect the shipped GLB animation and material, rather than the authoring scene."""
import bpy
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'Garran.glb'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
scene = bpy.context.scene
for track in rig.animation_data.nla_tracks:
    track.mute = True
rig.animation_data.action = next(a for a in bpy.data.actions if a.name.startswith('Idle'))
scene.frame_set(0)
camera_data = bpy.data.cameras.new('Preview')
camera = bpy.data.objects.new('Preview', camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera.location = (0, -4.5, 1.05)
camera.rotation_euler = (Vector((0, 0, .95))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 2.05
for name, pos, energy in [('Key', (2,-3,4),450), ('Fill',(-2,-2,2),280)]:
    data=bpy.data.lights.new(name,'AREA')
    light=bpy.data.objects.new(name,data)
    scene.collection.objects.link(light)
    light.location=pos
    light.rotation_euler=(Vector((0,0,.9))-light.location).to_track_quat('-Z','Y').to_euler()
    data.energy, data.size=energy, 3
scene.world=bpy.data.worlds.new('Preview World')
scene.world.color=(.08,.08,.08)
scene.render.engine='CYCLES'
scene.cycles.samples=20
scene.cycles.use_denoising=True
scene.render.resolution_x,scene.render.resolution_y=700,900
scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard'
scene.render.filepath=str(ROOT/'Garran-Idle.png')
bpy.ops.render.render(write_still=True)
rig.animation_data.action=next(a for a in bpy.data.actions if a.name.startswith('Walk'))
scene.frame_set(8)
scene.render.filepath=str(ROOT/'Garran-Walk.png')
bpy.ops.render.render(write_still=True)

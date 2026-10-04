"""Render the exported animation at native 1280 x 720, with a visible contact floor.

-- --motion also writes a local-only PNG sequence for the review movie.
"""
import bpy
import math
import sys
from pathlib import Path
from mathutils import Vector

PACKAGE = Path(__file__).resolve().parent
PREVIEWS = PACKAGE / 'Previews'
PREVIEWS.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30
bpy.ops.import_scene.gltf(filepath=str(PACKAGE / 'red-dragon-v1.3-animated.glb'))
rig = next(o for o in scene.objects if o.type == 'ARMATURE')
body = next(o for o in scene.objects if o.type == 'MESH')
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
shade = scene.display.shading
shade.light = 'STUDIO'
shade.studio_light = 'paint.sl'
shade.color_type = 'TEXTURE'
shade.show_shadows = True
shade.show_cavity = True
shade.cavity_type = 'BOTH'
shade.background_type = 'WORLD'
scene.world = bpy.data.worlds.new('Review World')
scene.world.color = (.045, .055, .075)
scene.display.render_aa = '8'
scene.view_settings.view_transform = 'Standard'
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.002))
floor = bpy.context.object
floor.name = 'Review Floor'
floor.color = (.19, .22, .25, 1)
# Thin visible ground lines make planted contacts and stride travel readable.
for axis in (0, 1):
    for index in range(-10, 11):
        location = [0, 0, 0]
        location[axis] = index * .2
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        line = bpy.context.object
        line.name = 'Ground Grid'
        line.scale = (.0015, 4, .001) if axis == 0 else (4, .0015, .001)
        line.color = (.3, .34, .38, 1)
bpy.ops.object.camera_add(location=(1.75, -2.4, 1.12))
camera = bpy.context.object
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 2.7
camera.rotation_euler = (Vector((0, -.05, .27)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
rig.hide_render = False

def select(name, frame):
    action = bpy.data.actions[name]
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    scene.frame_set(frame)

for name, frame in [('Walk', 15), ('Run', 7), ('ClawStrike', 30), ('FireBreath', 50), ('Fireball', 54), ('Roar', 30)]:
    select(name, frame)
    scene.render.filepath = str(PREVIEWS / (name + '.png'))
    bpy.ops.render.render(write_still=True)

if '--motion' in sys.argv:
    frames = PACKAGE / 'LocalReview' / 'frames'
    frames.mkdir(parents=True, exist_ok=True)
    sequence = [('Walk', 60, 2), ('Run', 30, 3), ('ClawStrike', 66, 1),
                ('FireBreath', 120, 1), ('Fireball', 150, 1)]
    output = 0
    for name, count, repeats in sequence:
        for repeat in range(repeats):
            for frame in range(count):
                select(name, frame)
                scene.render.filepath = str(frames / f'{output:04}.png')
                bpy.ops.render.render(write_still=True)
                output += 1
    print(f'REVIEW: {output} frames at 1280 x 720, 30 fps')

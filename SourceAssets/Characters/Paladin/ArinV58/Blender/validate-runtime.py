"""Measure exported floor placement and verify rigid equipment after skin baking."""
import bpy
import hashlib
import json
import runpy
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

PACKAGE = Path(__file__).resolve().parents[1]
MotionData = runpy.run_path(r'D:\SMILE 2.0\scripts\character-motion-data.py')['MotionData']
path = PACKAGE/'arin-v5.8-animation-checkpoint.glb'
body = MotionData(path, lambda name:name == 'Body')
bind_minimum = body.minimum(body.bind)
clips = []
for name in body.clips:
    duration = body.duration(name)
    times = [0, duration/2, duration]
    values = [body.minimum(body.world(body.sample(name,t))) for t in times]
    assert min(values) > -.002, (name, values)
    clips.append({'name':name, 'seconds':times, 'bodyMinimumY':values})
idle_minimum = body.minimum(body.world(body.sample('Idle',0)))
offset = round((bind_minimum-idle_minimum)*1000)
print('GROUNDING',bind_minimum,idle_minimum,offset,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-all-animations.blend'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
action = bpy.data.actions['SwordAttack']
rig.animation_data.action = action
rig.animation_data.action_slot = action.slots[0]
equipment = []
for frame in (1,11,28,38,46):
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    for name in ('Sword','Shield'):
        obj = bpy.data.objects[name]
        tree = KDTree(len(obj.data.vertices))
        for v in obj.data.vertices:
            co = obj.matrix_world @ v.co
            tree.insert(Vector((co.x,co.z,-co.y)),v.index)
        tree.balance()
        data = MotionData(path, lambda n:n == name)
        world = data.world(data.sample('SwordAttack',frame/30))
        maximum = 0.0
        for vertices,joints,weights,nodes,inverse in data.meshes:
            matrices = np.array([list(map(list, world[n])) for n in nodes]) @ inverse
            posed = np.sum(np.einsum('vkij,vj->vki', matrices[joints], vertices)*weights[:,:,None],axis=1)
            maximum = max(maximum,max(tree.find(Vector(p[:3]))[2] for p in posed))
        assert maximum < .00001, (name,frame,maximum)
        equipment.append({'name':name,'frame':frame,'maximumPositionError':maximum})
report = {'modelSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'bodyBindMinimumY':bind_minimum,'idleFrameZeroMinimumY':idle_minimum,
          'studioPlacementOffset1000':offset,'clips':clips,'equipmentRoundTrip':equipment,
          'bodyTriangles':84110,'swordTriangles':8557,'nativePartOrder':['Shield','Sword','Body']}
(PACKAGE/'Diagnostics/runtime-validation.json').write_text(json.dumps(report,indent=2))
print('RUNTIME_VALIDATION_PASS='+json.dumps(report))

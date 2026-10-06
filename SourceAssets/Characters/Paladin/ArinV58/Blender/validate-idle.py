import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p/'Blender/arin-v5.8-idle-review.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');body=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('ArinV58.')]
report={'frames':{},'bodyTriangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons)for o in body),'allBodyVerticesWeighted':all(any(g.weight>0 for g in v.groups)for o in body for v in o.data.vertices),'sourceSha256':hashlib.sha256((p/'Source/arin-v5.8.original.glb').read_bytes()).hexdigest()}
for frame in [1,39,77]:
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();gap=0;minimum=math.inf
 for o in body:
  ev=o.evaluated_get(deps);mesh=ev.to_mesh();duplicate={}
  for original,posed in zip(o.data.vertices,mesh.vertices):
   position=ev.matrix_world@posed.co;minimum=min(minimum,position.z)
   if o.name.endswith(('tripo_part_2','tripo_part_3')):
    key=tuple(round(c,6)for c in original.co)
    if key in duplicate:gap=max(gap,(position-duplicate[key]).length)
    else:duplicate[key]=position
  ev.to_mesh_clear()
 report['frames'][frame]={'bodyMinimumZ':minimum,'maximumHandSeamGap':gap}
 assert gap<.00002,(frame,gap)
# Import pristine geometry only for correspondence validation; do not save it.
old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p/'Source/arin-v5.8.original.glb'))
new=[o for o in bpy.data.objects if o not in old and o.type=='MESH'];deltas=[]
for source in new:
 candidate=next(o for o in body if o.name=='ArinV58.'+source.name)
 assert len(source.data.vertices)==len(candidate.data.vertices)
 assert [tuple(f.vertices)for f in source.data.polygons]==[tuple(f.vertices)for f in candidate.data.polygons]
 deltas.extend((candidate.matrix_local@v.co-source.matrix_world@s.co).length for v,s in zip(candidate.data.vertices,source.data.vertices))
report['maximumRestGeometryDifference']=max(deltas)
assert report['maximumRestGeometryDifference']<.000001
assert report['bodyTriangles']==84110 and report['allBodyVerticesWeighted']
(p/'Diagnostics/idle-validation.json').write_text(json.dumps(report,indent=2))
print('CANDIDATE_VALIDATION='+json.dumps(report))

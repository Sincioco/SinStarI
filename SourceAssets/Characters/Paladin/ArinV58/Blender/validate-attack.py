import bpy,json,hashlib,runpy
from pathlib import Path
from mathutils import Matrix
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p/'Blender/arin-v5.8-attack-review.blend'))
helpers=runpy.run_path(str(p/'Blender/prepare-idle.py'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
body=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('ArinV58.')]
approved=json.loads((p/'Diagnostics/idle-approved-grip.json').read_text())
minimum=1.0;drift=0.0
for frame in range(1,47):
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
 minimum=min(minimum,helpers['minimum'](body))
 for e in approved['equipment']:
  o=bpy.data.objects[e['name']];hand=rig.matrix_world@rig.pose.bones[e['bone']].matrix;relative=hand.inverted()@o.matrix_world
  drift=max(drift,max(abs(relative[r][c]-e['handRelativeMatrix'][r][c])for r in range(4)for c in range(4)))
assert minimum>=-1e-6,(minimum,drift)
assert drift<1e-5,(minimum,drift)
assert hashlib.sha256((p/'Blender/arin-v5.8-idle-approved.blend').read_bytes()).hexdigest()==approved['checkpointSha256']
report=json.loads((p/'Diagnostics/attack-validation.json').read_text())
report['reopenedFileValidation']={'samples':46,'minimumBodyZ':minimum,'maximumHandRelativeMatrixDrift':drift,'approvedIdleCheckpointUnchanged':True}
(p/'Diagnostics/attack-validation.json').write_text(json.dumps(report,indent=2))
print('SAVED_ATTACK_VALIDATION='+json.dumps(report['reopenedFileValidation']))

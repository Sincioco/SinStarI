"""Build v5.8's isolated full clip set from Sin's approved Idle equipment grip.

Original Attack is copied exactly. Collision trials and old calibrations are
excluded. Raw motion is retargeted with the same owner used for original Attack.
"""
import bpy
import hashlib
import json
import runpy
import struct
import sys
from pathlib import Path
from mathutils import Matrix, Vector

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from face_weights import repair_face_weights
from finalize_export import finalize_export
OUTPUT = PACKAGE/'arin-v5.8-animation-checkpoint.glb'


def main():
    helper = runpy.run_path(str(PACKAGE/'Blender/prepare-idle.py'))
    approved = json.loads((PACKAGE/'Diagnostics/idle-approved-grip.json').read_text())
    checkpoint = PACKAGE/'Blender/arin-v5.8-idle-approved.blend'
    assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == approved['checkpointSha256']
    bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
    scene = bpy.context.scene
    rig = next(o for o in scene.objects if o.type == 'ARMATURE')
    scene.frame_set(1)
    bpy.context.view_layer.update()
    base_location = rig.location.copy()
    finger_pose = {b.name:b.rotation_quaternion.copy() for b in rig.pose.bones
                   if not b.name.startswith('mixamorig:')}
    props = [bpy.data.objects[e['name']] for e in approved['equipment']]
    bases = {o.name:o.matrix_basis.copy() for o in props}
    relatives = {e['name']:Matrix(e['handRelativeMatrix']) for e in approved['equipment']}
    body = [o for o in scene.objects if o.type == 'MESH' and o.name.startswith('ArinV58.')]
    face_report = repair_face_weights(body)
    (PACKAGE/'Diagnostics/face-weight-repair.json').write_text(json.dumps(face_report,indent=2))
    # One skinned body part preserves Studio's Shield / Sword / Body contract.
    bpy.ops.object.select_all(action='DESELECT')
    for o in body:
        o.select_set(True)
    bpy.context.view_layer.objects.active = body[0]
    bpy.ops.object.join()
    body = [bpy.context.object]
    body[0].name = 'Body'
    idle = rig.animation_data.action
    idle.use_fake_user = True
    manifest = json.loads((PACKAGE/'arin-v5.8-animation-set.json').read_text())
    reports = []
    actions = {}
    for entry in manifest['animations']:
        name = entry['name']
        helper['action_for'](rig, None)
        rig.location = base_location
        if name == 'Idle':
            action = idle
            helper['action_for'](rig, action)
        elif name == 'SwordAttack':
            with bpy.data.libraries.load(str(PACKAGE/'Blender/arin-v5.8-attack-review.blend'), link=False) as (source, target):
                target.actions = ['SwordAttack']
            action = target.actions[0]
            helper['action_for'](rig, action)
        else:
            action = helper['load_motion'](rig, PACKAGE/entry['file'], name, finger_pose)
        action.use_fake_user = True
        start, end = map(round, action.frame_range)
        scene.frame_start, scene.frame_end = start, end
        scene.frame_set(start)
        bpy.context.view_layer.update()
        first_minimum = helper['minimum'](body)
        # Match the original Attack's whole-actor floor handling; never alter
        # limb rotations to resolve the artist's deferred pose collisions.
        baseline = base_location.z - first_minimum if name not in ('Idle','SwordAttack') else base_location.z
        samples = []
        maximum_drift = 0.0
        maximum_lift = 0.0
        for frame in range(start, end+1):
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            raw_minimum = helper['minimum'](body)
            if name not in ('Idle','SwordAttack'):
                rig.location.z = baseline
                bpy.context.view_layer.update()
                raw_minimum = helper['minimum'](body)
                lift = max(0, -raw_minimum)
                maximum_lift = max(maximum_lift, lift)
                rig.location.z = baseline + lift
                rig.keyframe_insert('location', frame=frame)
                bpy.context.view_layer.update()
            for obj in props:
                assert max(abs(obj.matrix_basis[r][c]-bases[obj.name][r][c])
                           for r in range(4) for c in range(4)) < 1e-7
                hand = rig.matrix_world @ rig.pose.bones[obj.parent_bone].matrix
                relative = hand.inverted() @ obj.matrix_world
                maximum_drift = max(maximum_drift, max(abs(relative[r][c]-relatives[obj.name][r][c])
                                                      for r in range(4) for c in range(4)))
            if frame in (start, (start+end)//2, end):
                samples.append({'frame':frame,'bodyMinimumZ':helper['minimum'](body)})
        if name == 'Idle':
            # Store the already approved constant object placement explicitly.
            for frame in (start,end):
                scene.frame_set(frame)
                rig.location = base_location
                rig.keyframe_insert('location',frame=frame)
        assert maximum_drift < .00001
        actions[name] = action
        reports.append({'name':name,'frames':[start,end],'source':entry['file'],
                        'bodySamples':samples,'maximumEquipmentMatrixDrift':maximum_drift,
                        'firstBodyMinimumZBeforePlacement':first_minimum,
                        'maximumFloorContactLift':maximum_lift,
                        'originalAttackCopied':name=='SwordAttack'})
        print('CLIP_READY='+json.dumps(reports[-1]),flush=True)
    for action in list(bpy.data.actions):
        if action not in actions.values():
            bpy.data.actions.remove(action)
    # Library imports can temporarily occupy the intended name with a donor action.
    for name, action in actions.items():
        action.name = name
    helper['action_for'](rig, actions['TownIdle'])
    for frame in (1, 31, 61):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        for side in ('Left', 'Right'):
            hand = rig.pose.bones[f'mixamorig:{side}Hand'].head
            shoulder = rig.pose.bones[f'mixamorig:{side}Arm'].head
            assert shoulder.z - hand.z > .15, (side, frame, list(hand), list(shoulder))
    for o in props:
        o.name = 'Shield' if o.name.startswith('Shield') else 'Sword'
    helper['action_for'](rig, actions['Idle'])
    scene.frame_start, scene.frame_end = 1,77
    scene.frame_set(1)
    bpy.context.view_layer.update()
    scene['Candidate'] = 'Arin v5.8 — all clips; approved Idle grip; original Attack retained'
    scene['Deferred'] = 'Sin will correct pose collisions manually in Studio'
    rig.hide_set(False)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [rig,*body,*props]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.wm.save_as_mainfile(filepath=str(PACKAGE/'Blender/arin-v5.8-all-animations.blend'))
    runpy.run_path(str(PACKAGE/'Blender/export-runtime.py'), run_name='__main__')
    runpy.run_path(str(PACKAGE/'Blender/prepare-flame-sockets.py'), run_name='__main__')
    gltf = finalize_export(OUTPUT)
    data = OUTPUT.read_bytes()
    exported=[a['name'] for a in gltf.get('animations',[])]
    assert set(exported)==set(actions),exported
    report={'clips':reports,'exportedClips':exported,'sourceGripSha256':approved['checkpointSha256'],
            'modelSha256':hashlib.sha256(data).hexdigest(),
            'calibrationImported':False,'collisionTrialsApplied':False,
            'meshes':[(m.get('name'),len(m['primitives'])) for m in gltf['meshes']]}
    (PACKAGE/'Diagnostics/animation-set-validation.json').write_text(json.dumps(report,indent=2))
    print('ANIMATION_SET='+json.dumps(report),flush=True)


if __name__ == '__main__':
    main()

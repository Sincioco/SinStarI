"""Milo-specific, editable canine action authoring. No runtime procedural motion."""
import bpy
import math
from mathutils import Matrix, Quaternion, Vector

CLIPS = [('Idle', 91), ('Walk', 37), ('Run', 25), ('Attack', 37),
         ('Defend', 31), ('Hit', 25), ('Death', 67), ('Victory', 91)]


def smooth(value):
    value = max(0, min(1, value))
    return value * value * (3 - 2 * value)


def points(body):
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    evaluated.to_mesh_clear()
    return result


def rotate(rig, name, axis, degrees):
    rest = rig.data.bones[name].matrix_local.to_quaternion()
    rig.pose.bones[name].rotation_quaternion = rest.inverted() @ Quaternion(axis, math.radians(degrees)) @ rest


def aim(rig, name, head, tail):
    rest = rig.data.bones[name]
    delta = (rest.tail_local - rest.head_local).rotation_difference(tail - head)
    rig.pose.bones[name].matrix = Matrix.Translation(head) @ delta.to_matrix().to_4x4() @ rest.matrix_local.to_quaternion().to_matrix().to_4x4()
    bpy.context.view_layer.update()


def limb(rig, prefix, side, dy, lift):
    upper, lower, paw = [prefix + part + side for part in ['Upper', 'Lower', 'Paw']]
    bpy.context.view_layer.update()
    start = rig.pose.bones[upper].head.copy()
    target = rig.data.bones[paw].head_local + Vector((0, dy, lift))
    if prefix == 'Hind':
        target += rig.data.bones['HindAnkle'+side].head_local - rig.data.bones[paw].head_local
    l1, l2 = rig.data.bones[upper].length, rig.data.bones[lower].length
    direction = target - start
    distance = min(direction.length, (l1 + l2) * .9999)
    direction.normalize()
    a = (l1*l1 - l2*l2 + distance*distance) / (2*distance)
    height = math.sqrt(max(0, l1*l1-a*a))
    bend = Vector((0, -1 if prefix == 'Hind' else 1, 0))
    bend = (bend - direction * bend.dot(direction)).normalized()
    joint = start + direction*a + bend*height
    end = start + direction*distance
    aim(rig, upper, start, joint)
    aim(rig, lower, joint, end)
    if prefix == 'Hind':
        ankle = 'HindAnkle'+side
        next_end = end + rig.data.bones[ankle].tail_local - rig.data.bones[ankle].head_local
        aim(rig, ankle, end, next_end)
        end = next_end
    aim(rig, paw, end, end + rig.data.bones[paw].tail_local - rig.data.bones[paw].head_local)


def build_actions(rig, body):
    scene = bpy.context.scene
    scene.render.fps = 30
    rig.animation_data_create()
    actions, report = [], {'units': 'meters; Blender Z becomes runtime Y', 'sampleRate': 30,
                           'bindMinimumY': min(v.co.z for v in body.data.vertices), 'clips': {}}
    for name, count in CLIPS:
        action = bpy.data.actions.new(name)
        rig.animation_data.action = action
        action.use_fake_user = True
        actions.append(action)
        samples = []
        for frame in range(1, count+1):
            scene.frame_set(frame)
            for b in rig.pose.bones:
                b.matrix_basis = Matrix.Identity(4)
            t = (frame-1)/(count-1)
            if frame == count and name in ['Idle', 'Walk', 'Run']:
                t = 0.0
            wave = math.sin(t*math.tau)
            root = rig.pose.bones['Root']
            legs = {(p,s): [0., 0.] for p in ['Front','Hind'] for s in ['L','R']}
            airborne = 0.
            if name == 'Idle':
                rotate(rig, 'Neck', (1,0,0), 1.2*wave)
                rotate(rig, 'Head', (0,0,1), 2*wave)
            elif name in ['Walk','Run']:
                run = name == 'Run'
                # Walk: four distinct footfalls. Run: paired diagonal trot with suspension.
                offsets = {('Front','L'):0, ('Hind','R'):.08 if run else .25,
                           ('Front','R'):.5, ('Hind','L'):.58 if run else .75}
                stance = .5 if run else .68
                stride = .10 if run else .055
                for key, offset in offsets.items():
                    phase = (t+offset) % 1
                    if phase < stance:
                        legs[key] = [-stride + 2*stride*phase/stance, 0]
                    else:
                        swing = (phase-stance)/(1-stance)
                        legs[key] = [stride-2*stride*smooth(swing), (.07 if run else .045)*math.sin(math.pi*swing)]
                root.location.z = -.025 + .006*math.cos(t*math.tau*2)
                rotate(rig, 'Chest', (1,0,0), (2 if run else .6)*wave)
                rotate(rig, 'Neck', (1,0,0), (-2 if run else -.6)*wave)
                if run:
                    airborne = .016 * max(0, math.sin(t*math.tau*2))**2
            elif name == 'Attack':
                wind = math.exp(-((t-.18)/.12)**2)*math.sin(math.pi*t)
                strike = math.exp(-((t-.48)/.14)**2)*math.sin(math.pi*t)
                root.location.y = .035*wind-.075*strike
                root.location.z = -.04*wind-.025*strike
                rotate(rig, 'Chest', (1,0,0), -6*wind+8*strike)
                rotate(rig, 'Neck', (1,0,0), -10*wind+19*strike)
                rotate(rig, 'Head', (1,0,0), 12*strike)
                for side in ['L','R']:
                    legs['Front',side] = [-.09*strike, .045*strike]
            elif name == 'Defend':
                brace = smooth(t/.65)
                root.location.z = -.085*brace
                root.location.y = .025*brace
                rotate(rig, 'Neck', (1,0,0), 15*brace)
                rotate(rig, 'Head', (1,0,0), -8*brace)
                for side in ['L','R']:
                    legs['Front',side][0] = -.045*brace
                    legs['Hind',side][0] = .025*brace
            elif name == 'Hit':
                recoil = smooth(t/.2) * (1-smooth((t-.2)/.8))
                root.location.y = .065*recoil
                root.location.z = -.055*recoil
                rotate(rig, 'Neck', (1,0,0), -18*recoil)
                rotate(rig, 'Head', (0,0,1), 10*recoil)
            elif name == 'Death':
                collapse = smooth(t/.45)
                roll = smooth((t-.25)/.5)
                root.location.z = -.15*collapse
                rotate(rig, 'Root', (0,1,0), 88*roll)
                rotate(rig, 'Neck', (1,0,0), 12*collapse)
                rotate(rig, 'Head', (0,0,1), -10*roll)
            elif name == 'Victory':
                greet = smooth(t/.2) * (1-smooth((t-.8)/.2))
                root.location.z = -.025*greet
                rotate(rig, 'Neck', (1,0,0), -8*greet)
                rotate(rig, 'Head', (0,0,1), 7*math.sin(t*math.tau*2)*greet)
                legs['Front','L'] = [-.055*greet, .095*greet]
            for i in range(1,4):
                wag = (16 if name == 'Victory' else 4) * math.sin(t*math.tau*(4 if name=='Victory' else 1)-(i-1)*.45)
                if name not in ['Idle','Walk','Run']:
                    wag *= math.sin(math.pi*t)
                rotate(rig, 'Tail'+str(i), (0,0,1), wag)
            for side, sign in [('L',1),('R',-1)]:
                rotate(rig, 'Ear'+side, (1,0,0), sign*2*wave)
            if name == 'Death':
                # After collapse the paws follow the rolling body into a held side pose.
                for side, sign in [('L',1),('R',-1)]:
                    for prefix in ['Front','Hind']:
                        rotate(rig, prefix+'Upper'+side, (1,0,0), (20 if prefix=='Front' else -28)*collapse)
                        rotate(rig, prefix+'Lower'+side, (1,0,0), (-35 if prefix=='Front' else 35)*collapse)
            else:
                for key, (dy,lift) in legs.items():
                    limb(rig, *key, dy, lift)
            bpy.context.view_layer.update()
            # Bake authored ground contact into the rig, preserving explicit run suspension.
            minimum = min(p.z for p in points(body))
            root.location.z += -minimum + airborne
            bpy.context.view_layer.update()
            posed = points(body)
            assert all(math.isfinite(c) for p in posed for c in p)
            low, high = [min(p[i] for p in posed) for i in range(3)], [max(p[i] for p in posed) for i in range(3)]
            assert low[2] > -.00001 and all(high[i]-low[i] < 1.8 for i in range(3)), (name, frame, low, high)
            samples.append({'frame':frame-1,'minimumY':round(low[2],7),'maximumY':round(high[2],7)})
            for b in rig.pose.bones:
                b.keyframe_insert('rotation_quaternion', frame=frame, group=b.name)
                b.keyframe_insert('location', frame=frame, group=b.name)
        report['clips'][name] = {'durationSeconds':(count-1)/30,'frames':samples}
    return actions, report

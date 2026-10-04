"""Original dragon performances. Blender-space metres, forward is -Y, up is Z."""
import math
from mathutils import Quaternion, Vector

CLIPS = {'Idle': 120, 'Walk': 60, 'Run': 30, 'Roar': 90,
         'FireBreath': 120, 'ClawStrike': 66, 'Hit': 24, 'Fireball': 150}
LOOPS = {'Idle', 'Walk', 'Run'}


def curve(t, keys):
    """Held endpoints, smoothstep between deliberately timed acting beats."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (a, x), (b, y) in zip(keys, keys[1:]):
        if t <= b:
            u = (t - a) / (b - a)
            return x + (y - x) * u * u * (3 - 2 * u)
    return keys[-1][1]


def rotate(rig, name, xyz):
    rest = rig.data.bones[name].matrix_local.to_quaternion()
    q = Quaternion()
    for axis, degrees in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), xyz):
        q = q @ Quaternion(axis, math.radians(degrees))
    rig.pose.bones[name].rotation_quaternion = rest.inverted() @ q @ rest


def translate(rig, name, xyz):
    rest = rig.data.bones[name].matrix_local.to_quaternion()
    rig.pose.bones[name].location = rest.inverted() @ Vector(xyz)


def foot_cycle(phase, stride, duty, lift):
    phase %= 1.0
    if phase < duty:
        # Linear rearward travel cancels the intended forward actor speed.
        return -stride / 2 + stride * phase / duty, 0.0
    u = (phase - duty) / (1 - duty)
    smooth = u * u * (3 - 2 * u)
    return stride / 2 - stride * smooth, lift * math.sin(math.pi * u) ** 1.4


def pose(rig, name, seconds, duration):
    t = seconds / duration
    wave = math.sin(t * math.tau)
    for b in rig.pose.bones:
        b.rotation_mode = 'QUATERNION'
        b.rotation_quaternion = Quaternion()
        b.location = (0, 0, 0)
        b.scale = (1, 1, 1)

    root = [0, 0, -.026]
    spine = [0, 0, 0]
    chest = [0, 0, 0]
    neck = [0, 0, 0]
    head = [0, 0, 0]
    jaw = 0
    wings = 0
    twist = 0
    tail_gain = 1
    foot_offsets = {k + s: [0, 0, 0] for k in ('Front', 'Hind') for s in ('L', 'R')}

    if name in LOOPS:
        root[2] += .003 * (1 - math.cos(t * math.tau))
        chest[0] = 1.5 * wave
        neck[0] = -1.0 * wave
        head[2] = 2 * math.sin(t * math.tau)
        jaw = .7 * (1 - math.cos(t * math.tau))

    if name in ('Walk', 'Run'):
        running = name == 'Run'
        duty = .5 if running else .72
        stride = .18 if running else .12
        lift = .065 if running else .038
        phases = ({'HindL': 0, 'HindR': .08, 'FrontL': .48, 'FrontR': .56}
                  if running else {'HindL': 0, 'FrontL': .25, 'HindR': .5, 'FrontR': .75})
        for limb, phase in phases.items():
            y, z = foot_cycle(t + phase, stride, duty, lift)
            foot_offsets[limb] = [0, y, z]
        root[2] = (-.054 + .016 * math.cos(t * math.tau * 2) if running
                   else -.035 + .004 * math.cos(t * math.tau * 4))
        root[0] = (.005 if running else .008) * wave
        spine = [(4 if running else 1.5) * wave, 0, 2.5 * wave]
        chest = [(-5 if running else -2) * wave, 0, -3.5 * wave]
        neck = [3 * wave, 0, 1.5 * wave]
        head = [-2 * wave, 0, -.5 * wave]
        wings = 8 if running else 4
        tail_gain = 1.8 if running else 1.3

    if name == 'Roar':
        inhale = curve(seconds, [(0, 0), (.55, 1), (.95, .6), (1.9, .5), (3, 0)])
        shout = curve(seconds, [(0, 0), (.55, 0), (.8, 1), (1.75, .85), (2.5, 0)])
        root[2] -= .012 * inhale
        root[1] = .02 * inhale
        spine[0] = -5 * inhale
        chest[0] = -7 * inhale + 3 * shout
        neck[0] = -13 * shout
        head[0] = 5 * shout
        jaw = 19 * shout
        wings = 17 * shout

    if name == 'FireBreath':
        inhale = curve(seconds, [(0, 0), (.65, 1), (.9, .25), (3.1, .25), (4, 0)])
        blast = curve(seconds, [(0, 0), (.65, 0), (.85, 1), (3.1, 1), (3.65, 0), (4, 0)])
        sweep = curve(seconds, [(0, 0), (.85, -1), (1.65, -.4), (2.45, .75), (3.1, 1), (4, 0)])
        root[1] = .018 * inhale - .022 * blast
        root[2] -= .018 * blast
        spine[0] = -4 * inhale + 4 * blast
        chest = [-5 * inhale + 6 * blast, 0, 4 * sweep]
        neck = [8 * blast - 8 * inhale, 0, 7 * sweep]
        head = [-3 * blast, 0, 3 * sweep]
        jaw = 17 * blast + 3 * inhale
        wings = 12 * blast + 4 * inhale
        tail_gain = 1.4

    if name == 'ClawStrike':
        wind = curve(seconds, [(0, 0), (.5, 1), (.78, .9), (1.0, 0), (2.2, 0)])
        strike = curve(seconds, [(0, 0), (.72, 0), (1, 1), (1.18, .85), (1.7, 0), (2.2, 0)])
        settle = curve(seconds, [(0, 0), (1.15, 0), (1.4, 1), (2.2, 0)])
        root[0] = -.018 * wind - .008 * strike
        root[1] = .025 * wind - .033 * strike
        root[2] -= .015 * wind + .022 * settle
        twist = -10 * wind + 14 * strike
        spine = [-3 * wind + 5 * strike, 0, twist * .45]
        chest = [-4 * wind + 6 * strike, 0, twist]
        neck = [2 * strike, 0, -twist * .55]
        head[2] = -twist * .3
        jaw = 7 * strike
        wings = 8 * wind + 12 * strike
        foot_offsets['FrontR'] = [-.015 * strike, -.075 * strike + .02 * wind,
                                   .035 * wind + .022 * strike]
        rotate(rig, 'WingRootR', (0, -10 - 12 * wind - 8 * strike, 12 + 14 * wind - 32 * strike))
        rotate(rig, 'WingArmR', (0, -10 * wind - 22 * strike, 18 - 5 * strike))
        tail_gain = 1.6

    if name == 'Hit':
        recoil = curve(seconds, [(0, 0), (.13, 1), (.26, .72), (.55, -.12), (.8, 0)])
        root[1] = .024 * recoil
        root[2] -= .014 * abs(recoil)
        spine[0] = -5 * recoil
        chest = [-9 * recoil, 0, 5 * recoil]
        neck = [6 * recoil, 0, -8 * recoil]
        head[0] = 8 * recoil
        jaw = 9 * max(0, recoil)
        wings = 8 * recoil

    if name == 'Fireball':
        charge = curve(seconds, [(0, 0), (.6, .35), (1.55, 1), (1.8, .1), (2.7, 0), (5, 0)])
        launch = curve(seconds, [(0, 0), (1.62, 0), (1.8, 1), (1.95, .45), (2.45, 0), (5, 0)])
        recover = curve(seconds, [(0, 0), (1.8, 0), (2.12, 1), (3.1, 0), (5, 0)])
        root[1] = .026 * charge - .025 * launch + .012 * recover
        root[2] -= .015 * charge + .012 * recover
        spine[0] = -4 * charge + 4 * launch
        chest[0] = -6 * charge + 8 * launch - 2 * recover
        neck[0] = -9 * charge + 16 * launch - 4 * recover
        head[0] = 2 * charge + 5 * launch
        jaw = 9 * charge + 22 * launch + 5 * recover
        wings = 13 * charge + 7 * launch

    translate(rig, 'Root', root)
    for bone, angles in [('Spine', spine), ('Chest', chest), ('Neck', neck), ('Head', head)]:
        rotate(rig, bone, angles)
    rotate(rig, 'Jaw', (jaw, 0, 0))
    # Small living overlap; attacks enter/leave the common resting pose.
    envelope = 1 if name in LOOPS else math.sin(math.pi * t) ** 2
    for side, sign in [('L', -1), ('R', 1)]:
        lag = (math.sin(t * math.tau - .45) + math.sin(.45)) * envelope
        if name != 'ClawStrike' or side != 'R':
            rotate(rig, 'WingRoot' + side, (0, -sign * (10 + wings + 2 * wave), sign * (12 + 2 * lag)))
            rotate(rig, 'WingArm' + side, (0, -sign * 2 * lag, sign * (18 + wings * .3 + 3 * lag)))
        rotate(rig, 'WingTip' + side, (0, sign * 4 * (math.sin(t * math.tau - .9) + math.sin(.9)) * envelope, 0))
    for i in range(1, 5):
        angle = ((math.sin(t * math.tau - i * .48) + math.sin(i * .48)) *
                 (1.5 + i) * tail_gain - twist * .23) * envelope
        # Lift the proximal tail above the crouching pelvis; distal overlap is lateral.
        rotate(rig, 'Tail' + str(i), (9 if i == 1 else 0, 0, angle))
    for limb, offset in foot_offsets.items():
        translate(rig, 'IK_' + limb, offset)

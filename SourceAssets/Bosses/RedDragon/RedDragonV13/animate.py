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


def recoil_wave(seconds, delay=0):
    """A sharp compression followed by a damped overshoot and settling rebound."""
    return curve(seconds - delay, [(0, 0), (.09, 1), (.2, .32), (.31, -.38),
                                   (.43, .18), (.55, -.07), (.65, 0)])


def appendages(rig, name, seconds, duration):
    """Independent arms and wings: flexed guard, purposeful strokes, delayed tips."""
    t = seconds / duration
    for side, sign in [('L', -1), ('R', 1)]:
        phase = t * math.tau + sign * .14
        lift, sweep, fold = 32.0, 30.0, 22.0
        upper, elbow, wrist, fingers = 32.0, 30.0, 12.0, 24.0
        arm_forward = 26.0
        wing_pitch = 0.0
        if name in LOOPS:
            # Visible flex instead of a permanently spread silhouette.
            pulse = math.sin(phase)
            lift += (7 if name == 'Idle' else 11) * pulse
            fold += 9 * math.sin(phase - .55)
            upper += (4 if name == 'Idle' else 12) * math.sin(phase + sign * 1.2)
            elbow += 8 * math.sin(phase + sign * 1.2 - .45)
            wrist += 7 * math.sin(phase - .8)
            fingers += 9 * math.sin(phase - .4)
        if name == 'Roar':
            beat = curve(seconds, [(0, 0), (.5, .25), (.82, 1), (1.2, -.35),
                                   (1.52, .8), (1.9, -.2), (2.3, .35), (3, 0)])
            lift += 29 * beat
            fold -= 25 * beat
            upper -= 18 * beat
            elbow -= 20 * beat
            fingers -= 24 * beat
        if name == 'FireBreath':
            beat = curve(seconds, [(0, 0), (.58, .7), (.85, -.5), (1.28, .85),
                                   (1.7, -.38), (2.13, .75), (2.55, -.32),
                                   (2.98, .65), (3.38, -.15), (4, 0)])
            lift += 32 * beat
            fold -= 24 * beat
            sweep -= 12 * beat
            upper += 8 * beat
            elbow += 12 * beat
            wrist -= 8 * beat
        if name == 'ClawStrike':
            wind = curve(seconds, [(0, 0), (.55, 1), (.77, 1), (1, 0), (2.2, 0)])
            strike = curve(seconds, [(0, 0), (.72, 0), (1, 1), (1.15, .9),
                                     (1.48, -.18), (1.75, .08), (2.2, 0)])
            if side == 'R':
                upper -= 32 * wind + 23 * strike
                elbow += 35 * wind - 45 * strike
                arm_forward += -34 * wind + 62 * strike
                wrist += 18 * wind - 34 * strike
                fingers += 15 * wind - 40 * strike
            else:
                elbow += 16 * wind + 12 * strike
                upper += 9 * strike
            lift += 25 * wind - 14 * strike
            fold -= 22 * wind + 12 * strike
            wing_pitch += sign * 8 * strike
        if name == 'Fireball':
            beat = curve(seconds, [(0, 0), (.8, .25), (1.55, 1), (1.85, -.55),
                                   (2.2, .38), (2.6, -.18), (3.1, .08), (3.6, 0), (5, 0)])
            lift += 32 * beat
            fold -= 27 * beat
            upper -= 12 * beat
            elbow += 20 * beat
            fingers += 14 * beat
        if name == 'Hit':
            shoulder = recoil_wave(seconds, .035)
            elbow_recoil = recoil_wave(seconds, .08)
            lift += (33 if side == 'R' else 27) * shoulder
            fold -= 28 * elbow_recoil
            wing_pitch = 18 * recoil_wave(seconds, .04) + sign * 3 * shoulder
            upper -= 26 * shoulder
            arm_forward -= 19 * shoulder
            elbow += 34 * elbow_recoil
            wrist -= 28 * recoil_wave(seconds, .11)
            fingers += 30 * recoil_wave(seconds, .13)
        rotate(rig, 'UpperArm' + side, (0, sign * upper, -sign * arm_forward))
        rotate(rig, 'Forearm' + side, (0, sign * 10, -sign * elbow))
        rotate(rig, 'Hand' + side, (0, sign * wrist, -sign * 8))
        rotate(rig, 'Claws' + side, (0, sign * fingers, 0))
        rotate(rig, 'WingRoot' + side, (wing_pitch, -sign * lift, sign * sweep))
        rotate(rig, 'WingArm' + side, (0, sign * (lift - 32) * .3, sign * fold))
        delayed = (math.sin(t * math.tau - .9) + math.sin(.9))
        envelope = 1 if name in LOOPS else math.sin(math.pi * t) ** 2
        tip = 8 * delayed * envelope
        if name == 'Hit':
            tip += 24 * recoil_wave(seconds, .12)
        rotate(rig, 'WingTip' + side, (0, sign * tip, sign * (-14 - (fold - 22) * .4)))


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
        foot_offsets['FrontR'] = [-.015 * strike, -.075 * strike + .02 * wind,
                                   .035 * wind + .022 * strike]
        tail_gain = 1.6

    if name == 'Hit':
        recoil = recoil_wave(seconds)
        root[1] = .035 * recoil
        root[2] -= .022 * max(0, recoil)
        spine[0] = -7 * recoil_wave(seconds, .02)
        chest = [-12 * recoil_wave(seconds, .04), 0, 7 * recoil_wave(seconds, .025)]
        neck = [11 * recoil_wave(seconds, .075), 0, -11 * recoil_wave(seconds, .08)]
        head = [12 * recoil_wave(seconds, .12), 0, 5 * recoil_wave(seconds, .13)]
        jaw = 13 * max(0, recoil_wave(seconds, .1))

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

    translate(rig, 'Root', root)
    for bone, angles in [('Spine', spine), ('Chest', chest), ('Neck', neck), ('Head', head)]:
        rotate(rig, bone, angles)
    rotate(rig, 'Jaw', (jaw, 0, 0))
    # Small living overlap; attacks enter/leave the common resting pose.
    envelope = 1 if name in LOOPS else math.sin(math.pi * t) ** 2
    appendages(rig, name, seconds, duration)
    for i in range(1, 5):
        angle = ((math.sin(t * math.tau - i * .48) + math.sin(i * .48)) *
                 (1.5 + i) * tail_gain - twist * .23) * envelope
        # Lift the proximal tail above the crouching pelvis; distal overlap is lateral.
        rotate(rig, 'Tail' + str(i), (9 if i == 1 else 0, 0, angle))
    for limb, offset in foot_offsets.items():
        translate(rig, 'IK_' + limb, offset)

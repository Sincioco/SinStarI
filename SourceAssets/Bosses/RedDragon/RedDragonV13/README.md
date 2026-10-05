# Red Dragon v1.3.1 — arms, wings and grounded creature animation

October 5, 2026. Studio's Red Dragon now uses this self-contained authoring package.
The preserved v1.1 and Vrax-retarget trial remain separate revisions.

Open `red-dragon-v1.3-rig.blend` to edit the live rig. `IK_FrontL/R` and
`IK_HindL/R` control the feet; `Pole_*` controls select each knee's bend plane.
Four new paw bones hold the claws level while two-bone IK bends each leg.
Front legs follow the chest, hind legs follow the root. Root/spine/chest,
neck/head/jaw, wings and tail have independent keyed performances.
The corrected rig has 36 deformation bones and eight authoring controls. Separate
`UpperArm`, `Forearm`, `Hand` and `Claws` chains move the arms independently of the
three-bone wing chains. Resting elbows bend and wrists drop below the shoulders;
the wings fold, stroke during attacks and react to hits. Studio receives
only baked deformation tracks; it does not evaluate Blender constraints.

| Clip | Duration | Intended performance |
| --- | --- | --- |
| Idle | 4 s | Bent arm guard, hand flex, breathing and independent wing movement |
| Walk | 2 s | Four-beat gait, 72% stance, separate foot lift and placement |
| Run | 1 s | Faster paired hind/front contacts, body compression and larger foot lift |
| Roar | 3 s | Inhale, body brace, neck extension, jaw opening and wing flare |
| FireBreath | 4 s | Inhale, forward brace, repeated wing strokes and neck sweep |
| ClawStrike | 2.2 s | Weight shift, independent arm wind-up/reach, wrist and claw flex |
| Hit | 0.8 s | Compression, delayed head/hand/wing recoil, overshoot and damped recovery |
| Fireball | 5 s | Charge, coordinated body/neck release, recoil and settling |

Idle, Walk and Run loop. Existing combat slot order and six named sockets remain
stable. Claw contact stays at 1.0 s, breath at 0.85–3.1 s, and fireball launch at
1.8 s. The descriptor keeps attacks non-looping for battle playback; standalone
Studio inspection can repeat clips through its existing playback policy.

In Studio, open **Characters → Dragon**, turn **Demo Off**, then select **Walk** or
**Run**. The timeline, speed controls, frame stepping and orbit remain available.
**Demo** exercises the coordinated battle; the Party Dragon scene uses the same
asset. These are in-place locomotion previews. Their authored travel speeds are
0.083333 and 0.36 Blender model units per second respectively. No navigation or
automatic world travel is introduced by selecting a clip.

## Rebuild and evidence

Run installed Blender with `--background --python build.py`, then `validate.py`.
The builder reads only `Source/` and writes this revision. Original geometry,
9,912 triangles, UVs, packed texture, scale and socket names are preserved.
The source rig and original/static GLBs, reference image and combat audio are
included. `animate.py` owns the performances; `build.py` owns rig/weight creation
and export; `validate.py` owns contact/export checks; `preview.py` owns review renders.

`validation.json` checks all 668 exported 30 Hz samples, finite coordinates, floor
clearance, planted feet, intended gait paths and exact loop closure. Maximum
foot-path error is approximately 0.0000246 model units; maximum stationary-foot
drift is approximately 0.0000163. The minimum body height differs from zero by
less than 0.000001. Bind minimum Z is zero, matching animated foot contact, so
no borrowed grounding offset is needed. Model hashes bind the reports to the GLB.
The arm regression fails on the prior package's missing independent joints.
It also measures deformed hand/wing movement relative to the chest, so torso
movement cannot disguise frozen appendages. Idle wrists sit over 0.10 model
units below their shoulders. Hit peaks at 0.133 s in the chest and 0.2 s in the
head and wrist, reverses direction, and settles to its exact starting pose.

`Previews/` contains actual exported-mesh renders. `preview.py -- --motion`
generates a local-only 1280 × 720 / 30 fps sequence; the corresponding 24.6-second
review MP4 remains in ignored `LocalReview/`. Videos are never committed.
Rebuild Studio using `tools/Character3DViewer/Build.ps1 -Target Native`, then use
its `Launch.ps1`. The game project declares this same package for its next build.

Native verification on October 5: `test-character-3d-viewer-hardening.ps1
-NativeOnly` passed, including calibration isolation and 59 graphics/input/audio
checks. Studio published 401 verified assets and was relaunched through
`Launch.ps1 -Build`. The first review covered Walk, Run and Party Dragon but missed
the T-pose hands and insufficient wing/recoil performance. The v1.3.1 review adds
Idle, repeated Fire Breath wing strokes, Claw Strike reach, Fireball release,
and the Hit compression/rebound in Studio.
`Studio-*.png` files record native inspection. Focused SMILE formatting and
both repository diff checks passed. The game declaration is aligned; the separate
game executable was not rebuilt for this Studio milestone.

`checksums.json` records all delivered package files except itself, Blender
backup files and ignored local review media. Regenerate it after an accepted edit.

## Scope and assessment

This removes the demonstrated fixed-leg mannequin behavior and gives the Dragon
an editable full-body animation workflow. Ground contacts and loop boundaries
are measured; readable poses are reviewed from the exported mesh and in Studio.
The existing angular wing topology and open-mouth shape remain visible. Flight,
terrain-adaptive runtime IK, facial animation and a new navigation controller
are outside this walking/running/attack milestone. Film-quality skin and wing
membrane deformation would require a separate topology/art pass.

See [the creation and repair journey](DRAGON-CREATION-AND-REPAIR-JOURNEY.md) for
references, iteration failures and the lessons that must survive future edits.

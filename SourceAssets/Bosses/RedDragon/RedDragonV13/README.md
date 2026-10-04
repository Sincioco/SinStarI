# Red Dragon v1.3 — grounded creature animation

October 5, 2026. Studio's Red Dragon now uses this self-contained authoring package.
The preserved v1.1 and Vrax-retarget trial remain separate revisions.

Open `red-dragon-v1.3-rig.blend` to edit the live rig. `IK_FrontL/R` and
`IK_HindL/R` control the feet; `Pole_*` controls select each knee's bend plane.
Four new paw bones hold the claws level while two-bone IK bends each leg.
Front legs follow the chest, hind legs follow the root. Root/spine/chest,
neck/head/jaw, wings and tail have independent keyed performances.
The rig has 28 deformation bones and eight authoring controls. Studio receives
only baked deformation tracks; it does not evaluate Blender constraints.

| Clip | Duration | Intended performance |
| --- | --- | --- |
| Idle | 4 s | Breathing, neck counter-motion and delayed wings/tail |
| Walk | 2 s | Four-beat gait, 72% stance, separate foot lift and placement |
| Run | 1 s | Faster paired hind/front contacts, body compression and larger foot lift |
| Roar | 3 s | Inhale, body brace, neck extension, jaw opening and wing flare |
| FireBreath | 4 s | Inhale, forward brace, neck sweep and controlled recovery |
| ClawStrike | 2.2 s | Weight shift, wind-up, wing-hand sweep, reaching forefoot and recovery |
| Hit | 0.8 s | Fast torso recoil with slower recovery and planted feet |
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
drift is approximately 0.0000084. The minimum body height differs from zero by
less than 0.000001. Bind minimum Z is zero, matching animated foot contact, so
no borrowed grounding offset is needed. Model hashes bind the reports to the GLB.

`Previews/` contains actual exported-mesh renders. `preview.py -- --motion`
generates a local-only 1280 × 720 / 30 fps sequence; the corresponding 18.2-second
review MP4 remains in ignored `LocalReview/`. Videos are never committed.
Rebuild Studio using `tools/Character3DViewer/Build.ps1 -Target Native`, then use
its `Launch.ps1`. The game project declares this same package for its next build.

Native verification on October 5: `test-character-3d-viewer-hardening.ps1
-NativeOnly` passed, including calibration isolation and 59 graphics/input/audio
checks. Studio published 401 verified assets and was relaunched through
`Launch.ps1 -Build`. Live review covered Walk, Run, Party Dragon, the claw contact
pose near 1.0 s, the fire-breath mouth attachment and fireball release. The three
`Studio-*.png` files record native attack inspection. Focused SMILE formatting and
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

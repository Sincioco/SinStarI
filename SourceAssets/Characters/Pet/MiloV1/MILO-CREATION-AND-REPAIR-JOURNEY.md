# Milo v1 — creation and repair journey

## October 6, 2026: original canine rig for Studio

Sin supplied `Milo - 4K - Low Poly - No Lighting.zip` from Tripo3D and requested
a Studio character tab plus Walk, Run, Attack, Defend, Hit, Death and Victory.
The untouched ZIP, FBX and 4096-square JPEG are retained in `Original`.
This package is owned by the independent SinStarI repository.

`build_milo.py` runs in installed Blender 5.2.1 and creates the self-contained
`milo-v1-rig.blend`, with packed texture and editable actions, and the runtime
`milo-v1-animated.glb`. `milo_motion.py` authors original canine motion rather
than retargeting a humanoid. No external downloads or dependencies are needed.

The mesh remains 5,241 source vertices and 9,502 triangles. Only its sub-micrometer
initial floor displacement is removed; no remeshing, model replacement or UV
change occurs. Smooth shading and a nonmetallic rough material retain the source
color texture. Armor and fur are part of the original combined surface, so armor
follows that skin; it is not detachable Studio equipment.

The 25-bone hierarchy includes a root, pelvis, spine, chest, neck, head, two ears,
three tail segments, three joints per front leg and four per hind leg. Blender
heat weights are normalized to four influences. Detached unweighted Tripo islands
receive the nearest weighted surface's skin, bounded to 7 cm; the transferred
vertex count is recorded in `milo-v1-package.json`. Every vertex must be weighted.

## Clip intent

| Clip | Intent |
| --- | --- |
| Idle | Gentle head movement and relaxed tail motion |
| Walk | In-place four-foot walking cycle with planted stance phases |
| Run | Faster diagonal trot with a small suspension phase |
| Attack | Anticipation followed by a forward head/body lunge and recovery |
| Defend | Lowered, braced stance, held at its end |
| Hit | Quick backward recoil, followed by recovery |
| Death | Collapse and side roll into a held ground pose |
| Victory | Raised greeting paw, head movement and stronger tail wag |

Idle, Walk and Run loop. Defend, Death and Victory hold their final frame in
Studio; Attack and Hit use the existing one-shot playback. These are authored
candidate animations ready for Sin's visual review, not a recorded approval.

## Grounding and validation

Blender Z becomes runtime Y. The bind minimum and Idle frame zero are both zero;
no Orin/Arin correction is copied. The builder measures all authored frames,
bakes ground contact into the root and preserves explicit Run suspension.
`grounding-and-motion.json` contains those per-frame measurements. The exported
GLB is independently re-imported by `preview_milo.py`, which asserts the eight
named clips and checks every integer frame for floor penetration greater than
2 mm. `export-validation.json` stores frame-zero, full-clip and final contacts.
Import at 30 fps before loading the GLB: importing into Blender's default 24 fps
scene and changing fps afterward creates fractional sample indices and a false
loop-seam report. At the correct 30 fps all contact samples remain within
0.0000003 meters of their intended plane; Run retains 0.016 meters of suspension.
The exported Idle, Walk and Run loops have zero first-to-last vertex displacement.
Animation export starts each action at time zero and retains sampled channels.
`Previews/animation-contact-sheet.png` is rendered from that re-imported GLB.

Studio uses profile 15 and character tab 17 with eight named inspection sockets.
No runtime grounding workaround, Party roster change or calibration save migration
is needed. The original humanoid pose-calibration editor is not enabled for Milo.
Any further pose refinement belongs in this Blender package until a canine editing
workflow is explicitly requested.

The focused native `tools/Character3DViewer/MiloTests.smileproj` in SMILE checks
the cooked model, all clips and sockets, frame submission and independent playback
of two Milo actors. Native Viewer hardening and the complete publication check
also pass. The full publication contains 403 runtime assets.

The first Studio launch exposed overly tight generic framing. Milo now uses a
75-percent fit margin. `MiloTests.CheckInitialFraming` projects all eight actual
model-bound corners at the default zoom and asserts clearance from the upper
navigation and lower timeline. This active regression protects the demonstrated
clipping issue; it does not change shared camera behavior.

## Rebuild

1. In background Blender, run `build_milo.py`, then `preview_milo.py` with
   `--python-exit-code 1`. These replace only this package's generated outputs.
2. Review the contact sheet and the two measured validation reports, especially
   neck/shoulder deformation, paw contact and the settled Death pose.
3. Build Studio through its normal `Build.ps1 -Target Native` route. The existing
   preparation script mirrors only the GLB and descriptor to ignored BuildAssets.
4. Compile/run the focused Milo native fixture in an isolated output directory,
   then launch through `Launch.ps1` and check the Characters → Milo tab.
5. Refresh `checksums.sha256` whenever accepted package outputs change. Do not
   overwrite Sin's later Blender edits by rerunning the original builder blindly.
   Package JSON uses CRLF, enforced locally by `.gitattributes`, so Git checkout
   preserves the descriptor and validation bytes used by those checksums.

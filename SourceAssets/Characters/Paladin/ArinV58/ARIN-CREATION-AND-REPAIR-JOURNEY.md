# Arin v5.8 — approved active character

Sin approved this model on October 6, 2026. The approved checkpoint was committed
and pushed before promotion: engine `ba133b2b`, game package `6215f516`.
Current native Characters, Party, battles and towns/game use v5.8. Earlier
inspection notes below describe the workflow leading to approval.

October 6, 2026. Sin supplied a completely new Tripo body generated from a
different reference image, especially the face. This is v5.8, not a denser
re-export of v5.7. Sin reports that the new source resolves the old model's holes.
Final deformation, equipment fit, and Studio acceptance remain subject to review.

## Ownership and preservation

- This independent SinStarI package owns the new body, its local rig, source
  references, equipment derivatives, Blender scene, previews, and measurements.
- `Source/arin-v5.8.original.glb` is an unchanged copy of
  `2026-10-06 0426 - Arin - T-Pose with Lighting.glb` from Downloads.
- The source has 84,110 triangles, 65,947 exported vertices, 113 meshes, one 4K
  base-color image, and no skeleton, weights, or animations.
- ArinV57 and its saved calibration remain intact. No v5.7 Studio calibration
  JSON, runtime saves, baked wrist corrections, or old attachment offsets are
  imported. The copied v5.7 neutral rig and raw Idle motion are reference inputs.
- Nothing is committed or pushed. Sin must inspect before authorizing either.
- At the initial inspection stage Studio still ran v5.7. v5.8 had not yet been
  installed into Studio, Party or the game. A distinct identity and
  empty calibration track must be established during that later integration.

## Rig and Idle preparation

`Blender/prepare-idle.py` prepares the candidate in background Blender 5.2.1.
The body and face vertices, polygon indices, and UVs remain those of the source.
The inspection rig has 55 bones, including separately fitted five-finger hands.
The 77-frame Idle at 30 fps derives from the raw calm Idle reference, retargeted
through armature-space rest/pose rotations rather than copied local wrist curves.

The first approximate donor transfer visibly distorted the arms and hands. It was
rejected. New arm landmarks and anatomical weights replace that transfer for the
arms. Hand heat weights are calculated on a temporarily welded proxy and copied
back to the untouched source vertices. Applying heat weights directly to the
split-seam source caused jagged gaps; the proxy resolves that demonstrated defect.
Do not restore either rejected approach.

The remaining torso/leg transfer uses the fitted donor surface, barycentric
weights, and recorded distance diagnostics. This is a candidate transfer between
different meshes, not the old exact-match v5.7 texture-restoration algorithm.
It still requires Sin's animation/deformation review. Finger curls are new v5.8
authoring values and are editable in Blender; they are not old Studio corrections.

`Diagnostics/idle-validation.json` records first/middle/last Idle contact,
coincident hand-seam continuity, weighted-vertex coverage, and exact unchanged
rest geometry. The current body has all 84,110 source triangles. Grounding uses
the new body's measured Idle minimum, not another character's standing offset.

## Equipment

The shield is the original v5.7 equipment geometry, fitted anew. Sword and shield
remain separate bone-parented objects so their local transforms can be edited in
Idle and carried along with their respective hand bones.

Sin identified the old sword's bent grip. `Blender/sword_geometry.py` straightens
the inherited grip/pommel and aligns the editable sword's axis. The measured
handle/blade angle changes from 5.636 degrees to effectively zero. Blade vertices,
topology, and UVs are preserved; the original equipment download remains intact.
This old sword is a fallback, superseded for the new candidate by Sin's new sword.

`Source/arin-v5.8-new-sword.original.glb` is the unchanged October 6 0446 sword
download. It contains 1,648,018 triangles and three 4K material images. Sin asked
to remove the side protrusions and reduce the result to 5,000–10,000 triangles.
`Blender/prepare-new-sword.py` owns that separate geometry cleanup; its report and
front/side previews must pass before the cleaned equipment is used in Idle.

The cleaned sword has **8,557 exported GLB triangles** (8,558 Blender faces;
99.48% reduction), no vertices beyond
the checked regular blade side profile, and no open blade boundary edges. Its
original three 4K material images remain embedded. The cleaned GLB is
`Equipment/arin-v5.8-sword.cleaned.glb`; the separate editable equipment scene is
`Blender/arin-v5.8-sword-cleaned.blend`. The main Idle scene uses this new sword,
scaled to 0.60 model units long. The old straightened sword/Idle scene remains in
`Blender/arin-v5.8-idle-old-sword.blend` as a local fallback.

### Known source limitation: decorative hilt topology

The original full-resolution sword already has 16 tiny open boundary edges and
20 edges with more than two incident faces after exact-position seam welding.
An isolated reduction preserves those counts. The cleaned output has 14 open
edges, all outside the blade. They are around the decorative guard/pommel, not
the removed blade protrusions. Source and output evidence is in
`Diagnostics/new-sword-cleanup.json`. No fully manifold sword is claimed.

This is retained for review: automatic global self-intersection/slit repairs
disturbed ornament topology, while the requested blade cleanup can preserve the
original hilt. If the tiny hilt defects become visible or a fully manifold asset
is needed, the concrete next step is local manual retopology of those decorative
regions, with UV/material and silhouette comparison against the untouched source.
Do not apply another global remesh or relax the blade's closure/profile checks.

## Review and next steps

Sin corrected the Idle sword and shield in Blender and authorized applying that
grip to primary Attack. `Blender/arin-v5.8-idle-approved.blend` preserves the live
artist checkpoint at frame 1; `Diagnostics/idle-approved-grip.json` records its
checksum, bone-relative matrices, and exact object/parent transforms. The Idle
review file also contains those saved edits. Do not rerun the preparation script
over either edited scene.

`Blender/prepare-attack.py` opens the artist checkpoint and retargets the primary
raw Slash 4 source using the same `load_motion` owner as Idle. It preserves the
approved local equipment transforms, all original mesh data, and the new finger
pose. It creates `Blender/arin-v5.8-attack-review.blend`, with `SwordAttack` active
at **frame 22** of frames **1–46**, plus Start/Strike/Recovery previews. Idle is
retained as an action and as its independent approved file. The script refuses
to overwrite an existing Attack review file, protecting later artist edits.

The raw transfer revealed boot penetration up to 0.0168004 model units. A v5.8-only
whole-actor vertical contact curve lifts penetrating samples while preserving
positive airborne height. Equipment inherits that actor transform. No old pose
calibrations or grounding offsets are used. The 46-sample check records zero hand
seam gap, hand-relative matrix drift below 0.0000003, and nonnegative body minima
after contact repair in `Diagnostics/attack-validation.json`.

## October 6: full v5.8 Studio review package

Sin approved the Idle grip and the original Attack transfer, then explicitly
rejected automated collision corrections after an unnatural wrist trial.
`arin-v5.8-attack-clearance-trial.blend` and its previews are rejected experiments.
They are not inputs to the full animation set. The original Attack review and
approved Idle checkpoint remain unchanged and retain their original checksums.

`Blender/prepare-animation-set.py` owns the complete derivative. It retains Idle,
appends the exact original SwordAttack action, and retargets the nine remaining
raw motion inputs through the existing `prepare-idle.py` motion owner. It preserves
the approved hand-relative equipment matrices, finger pose, geometry and UVs.
The 11 clips are Idle, Walk, Run, Defend, SwordAttack, SwordAttack2, BlockImpact,
Hit, Death, Victory and TownIdle. TownIdle is raw authored skeleton motion from
the old package, not its pose-calibration data. The manifest records all inputs.

The working Blender file is **Blender/arin-v5.8-all-animations.blend**. The older
attack-review file is an immutable comparison, so it still shows the original
face-weight defect. Use the all-animation scene or Studio for the repaired face.

### Lower-face skin repair

Both lower cheeks and the jawline had erroneous neck/shoulder/arm influence.
`Blender/face_weights.py` keeps the face, hair, eyes and mouth on Head and blends
the lower neck into Neck/Spine2. It changes weights only, not rest shape, UVs,
equipment calibration or skeletal animation. `validate-face.py` checks 2,135
face vertices on both sides through all 46 Attack frames against rigid Head
motion, and compares every Attack curve with the original action. The action
SHA-256 is `75361dd396ac5d597a19919e8e5fbc194fa98204c12d722ea17719faf8389a32`.
Close-up previews cover frames 11, 28 and 38 from both sides.

### Native export and floor placement

`Blender/export-runtime.py` keeps the full 84,110-triangle body, 8,557-triangle
sword and 216-triangle shield. Native part order is Shield 0, Sword 1, Body 2.
Equipment is baked into the same skin, weighted wholly to its respective hand;
the editable Blender scene remains bone-parented. `validate-runtime.py` compares
exported equipment vertices with the original review scene at five Attack frames.
Maximum positional error is below 0.000001 model units. Equipment sockets are derived
from the new rig/equipment, without old VFX attachment coordinates.

The body remains one part with 65,993 exported vertices. Sin explicitly requested
raising the native per-part limit to 100,000 rather than splitting the body.
The existing uint32 index format supports this; the associated per-part index
budget is now 300,000. Existing aggregate budgets remain unchanged. Source sword
textures stay 4K; runtime sword maps are 2K to fit the existing 256 MiB decoded
texture budget. The 4K body map is retained. Blender exports explicit tangents
for the source's degenerate UV corners without changing their topology.

The native cooker bakes mesh-node bind transforms into positions. The exported
skinned mesh nodes therefore cancel the rig's static root translation, avoiding
a second application of that translation. Skeleton motion and inverse binds are
unchanged. Measured body bind minimum Y is -0.0185309; animated Idle frame zero
is effectively 0. Studio's v5.8-only placement offset is -19 thousandths, derived
from this model rather than copied from Orin. Frame zero of every clip, midpoint
and end checks are recorded in `Diagnostics/runtime-validation.json`, including
Block/Hit contact and settled Death. The sampled subframe contact deviation is
below 0.0002 model units, within the existing 0.002 contact tolerance. Positive
airborne motion remains intentional.

### Independent Studio profile and manual work

The main **Arin** Characters tab now uses **Arin v5.8**; the temporary
comparison tab has been consolidated into it. Its own
canonical JSON is `Calibration/arin-v5.8-pose-calibration.json`; its checked profile
is `Calibration/arin-v5.8-profile.json`. Initial calibration has zero keys.
The runtime key is `CharacterViewer.Arin.v5.8.CalibrationKeyframes`, and the
in-memory bank is distinct from Arin v5.7 and Orin. The shared synchronizer accepts
`-Character ArinV58`. Launch and build include all three independent calibrations.
Sin's future saved/exported JSON is authoritative; never replace it with a seed.
Sin authorized promotion: Party, battle previews, Battle System and the game
now resolve the active Arin alias to this revision.
The new profile does not inherit v5.7 pose calibration. At Sin's request it reuses
the same blade fire and faint shield flames, with its own measured attachments.

Known pose collisions are deliberately retained at Sin's direction: sword hand
against left leg in Attack frames 27–30, sword against shield in 29–36, and shield
against left leg in 32–33. The next action is Sin's manual Studio correction and
saved per-clip keys. Do not resume automatic wrist or collision solving.

Focused native validation loads and draws all 11 clips, checks the 21-socket publication
and three parts, verifies calibration-bank isolation, and checks the 100,000
vertex/300,000 index boundaries. The native Studio publication is built separately
from the running application and must pass `Check-Publication.ps1` before launch.
The compiler/asset tool and native runtime were rebuilt for the raised limit.
No VSIX change or browser refresh is needed for this Studio review.


### TownIdle source-rest preservation and equipment flames

The first native review exposed extended arms in TownIdle. The intermediate FBX
had promoted its relaxed pose into the rest basis, so rest-delta transfer lost
the arm pose. The manifest now uses a skeleton/action-only `.blend` snapshot of
the original authored TownIdle. No old pose-calibration keys are imported.
The transfer checks both hands below their shoulders at frames 1, 31 and 61.
The exported TownIdle has 62 native samples. The original Attack curve checksum
still matches after this correction, and face/equipment/floor checks pass again.

`Blender/prepare-flame-sockets.py` measures the approved shield silhouette and
sword blade, producing 21 total sockets. It derives eight rim points and three
shield flame anchors from this equipment's geometry, then converts them through
the approved hand-relative transforms. Sword fire spans the cleaned blade beyond
the guard. The existing `ViewerEffects` flame/rim owners retain the accepted v5.7
appearance: strong blade fire and faint shield fire. v5.8 has independent weapon
and shield intensity slots, initially 100%; this does not change any pose key.
The descriptor and calibration identity are migrated together with the zero-key
working save, preserving the earlier snapshot as local recovery evidence.

### Active promotion and town locomotion

`PROFILE_ARIN` now aliases v5.8 index 16. Historical v5.7 stays at index 0;
its model, fingerprints and calibration bank are preserved. The former comparison
tab is consolidated into the main Arin tab. Sword and shield fire, audio and
all shared battle/Party owners follow the active profile. Game publication uses
the same model and metadata, with no game-specific animation implementation.

`scripts/retarget-town-locomotion.py -- Arin` retargets the established unarmed
Walk/Run into this package's ignored `Private/TownLocomotion/Arin-Town.glb`.
The accepted body, skin, materials and other clips are retained. Available bone
pairs are mapped by name, so older finger names are not required on this rig.
The accepted Idle floor is approximately -0.000000595; Walk/Run contact remains
within 0.00000002, with intended airborne motion retained. The checksum and
measurements are in `Calibration/town-locomotion-retarget.json`.

Text files follow the repository LF policy so package/descriptor checksums survive
a fresh checkout. Normalizing descriptor line endings changes its byte identity;
the profile and zero-key working calibration were migrated together after a
graceful Studio shutdown and live export. No pose values or animation data changed.

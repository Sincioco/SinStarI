# Arin v5.8 motion repair approval - October 6, 2026

Status: implemented, locally validated, and approved by Sin for commit and push.
Sin authorized publication after the local review handoff. The previous approved
checkpoints remain intact for rollback.

## Changes

- SwordAttack: arm-chain changes clear the reported hand/left-leg, sword/shield,
  and shield/left-leg collisions. Smooth corrections enter and leave the attack
  follow-through; timing, body/leg motion and local wrist orientations are retained.
- Victory: both arms move away from the hip/body, clearing gauntlet/equipment
  intersections, including the raised-equipment section.
- TownIdle: a small right-arm adjustment clears the sword hilt from hip armor.
- Equivalent quaternion signs are made consistent in those three clips to remove
  Blender interpolation spins. The other eight action curves are unchanged.
- Approved sword/shield hand transforms, geometry, skin weights, repaired face,
  clip names/counts, grounding correction and flame sockets are preserved.

## Validation actually performed

- Triangle BVH intersection checks passed 725 samples at half-frame intervals:
  SwordAttack 91, Victory 513, TownIdle 121. Checked both forearm/hand regions
  against legs, equipment against legs and torso/head, and sword against shield.
- Lowest sampled sword point: Attack 0.22151 m, Victory 0.44423 m,
  TownIdle 0.23999 m above the Blender floor.
- Geometry/skin weights and prop local transforms match the approved checkpoint.
  Every protected local rotation matches the approved keyed pose, allowing only
  equivalent quaternion signs. Eight other actions match exactly.
- Facial regression: 2,135 lower-face vertices on both sides follow Head through
  all 46 Attack frames; original Head/Neck curves retained.
- Export round-trip: sword/shield positions match Blender within 0.000000535 m
  at sampled Attack frames. Start/middle/end floor checks pass all 11 clips.
- Native ArinV58Tests passes actual loading/drawing, 11 clips, 21 sockets,
  three mesh parts, calibration isolation and native part-budget checks.
- Studio Release build and publication pass: 414 assets. Independent game
  Release build passes: 939 assets. Both cooked Arin models have SHA-256
  `969685729be304a0a41f78decc960e1b1690065d6a03b067e19dcef667319a31`.
- The private town derivative was regenerated; unarmed Walk/Run retain their
  existing grounding and source policy. The new source GLB SHA-256 is
  `a1e3f265d91e7ad25e154b25a8f90b9c45b2f834a1545272b5dee2286e44ce75`.
- Studio relaunched normally. Characters > Arin was opened, Attack paused at
  frame 27, and Frame > / < Frame verified 27 -> 28 -> 27. Pose panel shows
  zero saved v5.8 correction keys. Live/canonical calibration comparison passes.
- Game launched and Characters > Arin rendered successfully with both flame
  effects. The brief game check was closed normally; Studio remains for review.

## Review and rollback

At the review handoff, Studio was left on Arin's individual tab at Attack frame 27 with Demo off and the
Pose panel visible. Use `< Frame` / `Frame >`, hover-wheel over the timeline, or
scrub it. Sword Fire, Shield Fire and Glow are temporarily hidden for visibility;
their effects remain included and can be toggled back on. The dragon, grid and
reflective floor are hidden in this inspection session.

`Blender/arin-v5.8-approved-before-motion-repair.blend` preserves the approved
source. The exact prior GLB, descriptor, profile, calibration JSON and manifest
are also backed up at `D:\SMILE 2.0\artifacts\arin-v58-motion-repair\approved`.
The active local Blender file remains `Blender/arin-v5.8-all-animations.blend`.

Only `Profiles.smile`'s existing v5.8 fingerprint changes in engine source;
its line count is unchanged. Authoring/validation remain in two focused Blender
scripts (no new runtime solver, UI module, dependency, or architecture exception).
The existing face validator now protects Head/Neck curves instead of requiring
the deliberately edited full Attack action to remain identical.

These are sampled geometry checks and visual spot checks, not continuous
collision simulation. Sin subsequently authorized committing and pushing the
motion repair, then expanded publication to all current unstaged repository
changes. No additional rebuild or browser refresh is required for publication.

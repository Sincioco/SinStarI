# Arin v5.8 native Studio review

October 6, 2026. Candidate for Sin's manual pose corrections; no commit or push.

## Validated assets

- 11 clips, 21 sockets, 3 parts; 74,931 total exported vertices and 92,883 triangles.
- Body: 65,993 vertices / 84,110 triangles, retained as one part.
- New sword: 8,557 triangles. Original full-resolution source remains preserved.
- Approved Idle equipment matrices retained across every clip.
- Original Attack action checksum unchanged; rejected collision trials excluded.
- Both lower cheeks/jawline: 2,135 face vertices follow Head throughout all 46 Attack frames.
- Native skin export round-trips sword/shield points within 0.000001 model units.
- Grounding checks cover every clip's start, midpoint and end, including Block/Hit and settled Death.
- TownIdle uses its original rest basis; both hands remain below shoulders at sampled frames.

## Native and storage checks

- `ArinV58Tests`: actual load/draw of all clips, 21-socket publication, flame anchors,
  separate calibration banks, and accepted/rejected mesh-limit boundaries passed.
- `test-model3d-part-limit.ps1`: cooker accepts 100,000 vertices and rejects 100,001.
- Native runtime and compiler/asset tool rebuilt; no binary format change.
- Studio build/publication validation: 413 runtime assets.
- v5.8 canonical JSON and live save compare equal, with zero pose keys.
- v5.7 and Orin canonical JSON retained; Party roster remains v5.7.
- Studio visual review confirmed relaxed TownIdle, independent pose editor, blade fire
  and faint shield fire. Both flame toggles passed off/on checks after the final build.
  Weapon intensity changed to 79% and back to 100%; shield stayed at 100%. Studio
  remains open on v5.8 Idle, Demo off, both flames on and the camera fixed close up.

## Ownership and scope

Character-specific mesh repair, animation transfer, attachments, reports and source
checkpoints belong to this package. Profiles owns identity/grounding; calibration
owns the independent bank; ViewerEffects owns existing effects and separate intensity
slots; ViewerUi exposes existing controls. No new host-level feature algorithms.

Runtime/cooker limit edits have zero net line growth. Profile changes add about 46
lines, tab routing 18, calibration 2, effects 4, lifecycle 2 and UI 7; no architecture
limit was raised or exclusion introduced. No dedicated architecture guard script
was found. Focused source/diff review and `git diff --check` passed.

## Retained limitations

Sin will manually correct Attack hand/leg contact at frames 27–30, sword/shield
contact at 29–36 and shield/leg contact at 32–33. Automatic collision/wrist correction
is explicitly deferred. Tiny original sword-hilt seams are documented in the journey.
This is native review readiness, not acceptance of every pose or a promotion to Party.

Studio has been rebuilt by Codex; no user .NET rebuild, VSIX update or browser refresh
is needed. The editable Blender scene is `Blender/arin-v5.8-all-animations.blend`.

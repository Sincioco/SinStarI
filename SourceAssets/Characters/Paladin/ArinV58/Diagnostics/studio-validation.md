# Arin v5.8 approved native promotion

October 6, 2026. Sin approved the model. Engine `ba133b2b` and game `6215f516`
were committed and pushed before starting promotion, as requested.

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
- v5.7 and Orin canonical JSON retained; active Party roster now uses v5.8.
- Studio visual review confirmed relaxed TownIdle, independent pose editor, blade fire
  and faint shield fire. Both flame toggles passed off/on checks after the final build.
  Weapon intensity changed to 79% and back to 100%; shield stayed at 100%. Studio
  was inspected on v5.8 Idle with both flames on.

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

Sin will manually correct Attack hand/leg contact at frames 27Ã¢â‚¬â€œ30, sword/shield
contact at 29Ã¢â‚¬â€œ36 and shield/leg contact at 32Ã¢â‚¬â€œ33. Automatic collision/wrist correction
is explicitly deferred. Tiny original sword-hilt seams are documented in the journey.
Model promotion is approved; the known individual pose collisions remain for Sin to edit.

Studio has been rebuilt by Codex; no user .NET rebuild, VSIX update or browser refresh
is needed. The editable Blender scene is `Blender/arin-v5.8-all-animations.blend`.

## Promotion checks and discovered fixes

- Active Arin alias resolves to v5.8 while historical v5.7 retains index 0.
- Main Characters tab, Party/companion routing, Battle System, town roster and
  independent game publication use the same shared profile and versioned saves.
- Private town Walk/Run retarget uses the new body; skin/materials/non-locomotion
  clips are preserved. Grounding report is `Calibration/town-locomotion-retarget.json`.
- All 11 native clips, three parts, flame anchors and independent calibration
  banks pass. The added Party regression checks both active attack names against
  actual published clips. Live review had exposed an empty attack selection for
  v5.8; `Profiles.PartyAttackName` now recognizes the new revision.
- The flame adjustment API now accepts v5.8's intensity slots 8/9; the existing
  bounds regression covers all ten slots. Slider ownership remains unchanged.
- Native Neris route/scene, real party resources and zero-key v5.8 calibration
  pass (`neris-town-30b69556471640a5a9cf0fda75d72e68`).
- Historical v5.7 parser/accepted-pose tests and calibration isolation passed.
  They explicitly pin their generated active alias to v5.7; no historical pose
  fixture is transplanted onto v5.8. Active v5.8 has its own native regression.
- Initial hardening reported six assertions. After fixing active attack routing,
  updating expected version/bank/display values and intensity bounds, the focused
  hardening rerun passes, including architecture assertions and 59 native
  graphics/pointer/audio checks. An instrumented test helper initially recursed
  into itself; that temporary helper was corrected before the successful rerun.
- Game build initially rejected a missing `TownExportScene` shared source link.
  The game project now links the existing owner; no game implementation was copied.
- Final Release builds pass: Studio publishes 414 runtime assets; the native game
  publishes 939. Both publish identical v5.8 combat and town model bytes.
- Live native review confirms v5.8 in the main Arin tab, continued Party Dragon
  playback past Arin's turn, Battle System rounds and the game's Characters menu.
  Town playback was inspected with the new unarmed model; native town checks
  independently validate calibration and scene resources. The game was closed
  normally after inspection, with Studio left available for Sin's pose work.
- Git line-ending normalization corrected trailing carriage returns in the journey
  and aligns descriptor/package checksums with the declared LF checkout policy.
  The zero-key profile identity was migrated after live export and graceful closure.

Promotion changes stay with existing owners. Profiles has six net added lines,
NativeViewerTabs removes twelve; calibration, effects, lifecycle and session have
no net growth. The native profile test grows five lines and the historical harness
seven. No entry-point algorithm, dependency, architecture exclusion or limit change
was added. Existing oversized modules receive only local identity/range updates.

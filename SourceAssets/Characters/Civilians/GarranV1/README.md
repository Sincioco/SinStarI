# Garran v1 — Neris Town armory owner

Garran uses Sin's approved NPC1 weapon-shop-owner model and ImageGen-enhanced
texture. The original files and 4K masters remain under
`Assets/Characters/NPCs/Neris/NPC1 - Neris - Weapon Shop Owner`.

This package is the canonical animated game revision. `Source/Garran-Textured-T-Pose.glb`
is the approved 2K textured input; `Source/build_garran.py` adds a 14-bone skin and
bakes Idle (2 seconds) and Walk (32 frames at 30 fps). Garran remains behind the
counter and turns toward the party during conversation.
The Walk clip is retained as an authoring option; the shop uses Idle only.

The game GLB has one mesh/material and 10,460 triangles. One near-zero-area
triangle was removed because floating-point export collapsed it and SM3D
correctly rejected it. The original model was not modified. The texture is 2048²
for gameplay; the approved 4096² authoring images remain unchanged.

`Garran.blend` contains the editable rig, packed texture and animation sources.
`garran.sm3d.json` declares both loops. `grounding.json` records the GLB checksum,
bind height and every sampled clip's foot minimum; Idle frame zero and all Walk
samples are grounded within 0.0001 metres. `Source/preview_garran.py` checks the
exported GLB and creates front-facing Idle/Walk previews.

`Armory-Background.png` is the user-approved ImageGen background. Its original
resolution is 1672 × 941. `armory-prompt.txt` preserves the built-in ImageGen prompt.
It remains an authoring reference. This folder's `Armory-Room.glb`,
`Source/build_armory.py` and `Armory-Room.blend` preserve the previous seven-part
room. Studio and the game now render the rebuilt ivory/teal/brass room from
`SourceAssets/Towns/Neris/NerisWeaponShopV2`; that package owns its complete
360-degree Blender model, unique baked finishes and thirteen-part runtime cutaway.

Studio owns the shared behavior in `TownArmory`, room geometry/camera/collision in
`TownArmoryRoom`, conversation UI in `TownArmoryPanel`, and stock in
`TownArmoryCatalog`. The 3D scene fills the game window. Arin and all followers
enter and walk through the customer area using WASD; the wheel adjusts zoom.
Approach the counter and press E/Enter to speak. Garran turns toward the party,
then the greeting and catalog overlay the room. Escape first ends conversation;
Escape again or walking through the entrance returns the party to the exact
outdoor trail and travel settings. Moving away from the threshold rearms entry.
The authored town and its nine existing residents remain unchanged.

Purchases are a session-only demonstration: all six weapons can be bought without
a gold check. Confirmation and quantities are recorded in the active town scene.
No saved party inventory, equipment or gold is changed. The catalog is provisional.

Validation: run the game `Build.ps1`, then `Maps/Test-Armory.ps1`. Add `-Inspect`
for the interactive native acceptance window; its isolated application ID does
not alter the game's or Studio's saved maps.

Verified on 2026-10-08: native game build (979 assets), Studio build/publication
(418 assets), focused armory acceptance (45 checks, zero failures)
(including all four outdoor positions and travel settings), the existing 17-map
regression (zero failures), and five focused SMILE style checks. Native visual
review confirms the full-window room and readable conversation overlay with
Garran visible beside the catalog. Ownership and physical-line growth are recorded
in Studio's architecture notes. No dependencies, compiler changes, numeric-budget
exceptions or saved inventory were introduced. Purchases remain a prototype.

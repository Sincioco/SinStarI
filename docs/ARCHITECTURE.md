# Game ownership and local development

Sin Star I is developed at this repository's root. The independent sibling
`SMILE 2.0` checkout owns the compiler, runtime, libraries and Studio.
`Visual Script and Storyboard` remains the canonical story-production folder.

Studio is authoritative for Battle Systems, Battle Simulations, and Towns/Maps.
Sin develops these in Studio and brings the approved behavior and authored content
into the game. Shared implementations stay aligned; the game wraps them only for
its own navigation and lifecycle instead of maintaining divergent versions.

## Ownership

| Owner | Responsibility |
| --- | --- |
| `Program.smile` | Window lifecycle, title actions, screen delegation and shutdown. |
| `TitleScreen.smile` | Menu choices, selection and title presentation. |
| `Maps/MapBrowser.smile` | Thumbnail resources, pagination, selected map and gallery input. |
| `Maps/MapCatalog.smile` | Permanent-map names and incremental installation of packaged maps into the game's own save namespace. |
| `Maps/MapAssets.smile` | One bounded prepared record loaded and saved per frame. |
| `Maps/MapExploration.smile` | Game scene lifecycle and navigation back to the gallery. |
| Studio `TownEditorSession` | The authored document, terrain, map selection and existing persistence. `OpenForPlay` suppresses editing and automatic showcase changes for the game host. |
| Studio `NerisTown` and its existing collaborators | Rendering, collision, movement, followers, camera, day/night lighting and scene resources. Optional play-only input and overlay flags preserve ordinary Studio defaults. |
| `CharacterPresentation.smile` / Studio `ViewerWorkflow` | Game presentation navigation / shared actors, battle choreography and effects. |
| `Battle/BattleScreen.smile` | Game navigation, music and lifetime around Studio's native Battle System; retains its host for session EXP across title visits. |
| Studio `NativeViewerHost` and its battle collaborators | Party orders, Auto Battle, presentation, cameras, HUD, statistics, rewards and restart; game embedding disables Studio tab navigation. |
| Other `Battle/` modules | Shared battle rules, attacks, feedback and icons; the older arena implementation remains available in source. |

The game does not duplicate the Studio map simulation. Documents stay with their
existing owner; no reverse dependency into the game entry point was added.
The game application identity is `smile.game.sin-star-i`, separate from Studio's.

Arin v5.8 is the active native character. The shared `Profiles.PROFILE_ARIN`
alias selects his versioned model and calibration identity in all character,
battle and town consumers. The game project publishes the ArinV58 asset and
metadata; Studio build preparation supplies its private unarmed town variant.
ArinV57 and its accepted corrections remain historical, separate package data.

The battle wrapper passes its Viewer session to the existing host, which owns the
encounter and menu state. It does not copy the battle algorithms. Host navigation
defaults remain unchanged for Studio. The game reserves the former tab row for
returning to its title, lets nested menus consume Escape first, and defers window
closure while an inspector has unsaved edits. The game music owner stays active.

The Battle System integration adds three lifecycle lines to `Program.smile`
(141 to 144), keeps `TitleScreen.smile` at 409 lines, and changes the battle wrapper
from 97 to 111 lines. The shared native host grows from 471 to 506 lines for the
optional navigation boundary and read-only UI queries. No numeric guardrail or
exception changed. Existing native battle planning and real-asset scene checks
pass, as do the four focused style checks. Interactive checks cover order and
attack menus, nested Escape, statistics, Auto Battle, pause, camera return, panel
visibility, returning to the title and reopening the encounter.

## Maps and build inputs

The Neris weapon shop is shared Studio behavior. `TownArmory` owns the visit,
conversation, temporary outdoor-trail snapshot and demonstration purchases.
`TownArmoryRoom` owns static room resources, bounded floor movement and camera;
`TownArmoryPanel` owns the conversation overlay and `TownArmoryCatalog` owns stock.
`NerisTownParty.Interior` keeps the existing actor presentation on the flat room
floor with visible followers; outdoor defaults and navigation stay unchanged.
The game host suppresses its Back action and map HUD while the shop consumes input.
Leaving restores all outdoor trail positions and travel settings. The canonical
`SourceAssets/Characters/Civilians/GarranV1` package supplies the keeper, while
`SourceAssets/Towns/Neris/NerisWeaponShopV2` owns the rebuilt room and its complete
editable Blender model. Studio and game use the same thirteen-part cutaway export;
the room owner reserves clearance around its central display. No saved inventory
or authored resident changed.

`Prepare-Maps.ps1` reads the permanent catalog and the authored `.town` bundles
under `SourceAssets/Towns/Neris`. It verifies bundle and record checksums, then
prepares payload assets and a small record manifest in ignored `Assets/Maps`.
The game imports a record per frame using the existing executable-relative asset
reader and checked data store. This avoids a hardcoded machine path and needs no
compiler or runtime extension. Thumbnails are maintained in `Maps/Previews`.

`Build.ps1` links the shared Studio source inventory, prepares installed local
assets, and compiles the native executable. `BuildAssets`, generated assets and
native build outputs are ignored. Private/licensed authoring inputs stay local.
There are no new downloaded tools or package dependencies.

The legacy `SMILE 2.0/games/SinStarI` path is a local compatibility junction to
this root after migration. Existing Studio authoring scripts can use that path;
it must never become a second editable game copy. A new machine needs an equivalent
junction until those engine-side callers are explicitly migrated.

## Validation

```powershell
.\Build.ps1
.\Maps\Test-Maps.ps1
.\docs\Capture-Battles.ps1
```

The map regression uses its own application identity, tests unloaded thumbnails,
imports all 17 packaged maps, checks full party loading and movement, and verifies
that play mode stays on the selected map while idle. It also exports day/night
photographs to the test's evidence directory. Pass an explicit `-EvidenceDirectory`
to refresh the README's town images. The battle photograph fixture samples actual
action frames from a disposable instrumented copy of the shared presentation host.

No new general unit-test suite or architectural framework was introduced. The
repository's architecture review remains manual; size/dependency gates and numeric
baselines have not been invented or relaxed. Existing large Studio modules remain
legacy debt; this change adds only the game-host boundary needed for reuse.

## History and protected material

The migration retains the original game subdirectory's commit history as a merge
parent. Imported history excludes video files. The story repository's earlier
history and its production folder are preserved. Never stage or commit videos.

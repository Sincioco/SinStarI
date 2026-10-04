# Game ownership and local development

Sin Star I is developed at this repository's root. The independent sibling
`SMILE 2.0` checkout owns the compiler, runtime, libraries and Studio.
`Visual Script and Storyboard` remains the canonical story-production folder.

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
| `Battle/` | Game-owned turn-based battle rules, actors, feedback, UI and tests. |

The game does not duplicate the Studio map simulation. Documents stay with their
existing owner; no reverse dependency into the game entry point was added.
The game application identity is `smile.game.sin-star-i`, separate from Studio's.

## Maps and build inputs

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

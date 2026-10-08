# Validation — 2026-10-08

## Completed checks

- Blender 5.2.1: opened the saved master, inspected the complete shell and both
  cutaways, and made a full 24-step orbit. Saved a comfortable interior review view.
- Native model cooker and the compiler-bundled `smileasset inspect`: pass.
  13 parts, 12 materials, 130,261 vertices, 49,769 triangles, five textures;
  grounded floor top at zero. The earlier standalone asset tool was older than
  the compiler; final inspection uses the compiler's matching tool.
- Studio native build and publication verification: 423 assets, pass.
- Native Sin Star I `Build.ps1`: 984 assets, pass.
- `Maps/Test-Armory.ps1 -Inspect`: 46 passed checks, zero failures. Tests exercise
  the real authored doorway, full-town resource coexistence, four party members,
  pedestal collision, approach to the counter, keeper visibility/facing, six
  demonstration purchases, conversation Escape, exit, restored outdoor positions,
  travel settings, and re-entry. The native rendered interior was inspected.
- SMILE style checks: the ten road/cache/minimap files and five armory/party files
  pass. `git diff --check` passes. Architecture review is manual; no automated
  size or dependency gate is installed or claimed.

## Newly painted road regression

Studio saved the live authored Neris Town and its preview to
`artifacts/neris-road-flicker-20261008/2026-10-08 2220 - Neris Town - Before Fix.town`
before changes. The saved road brush spans X=70..920 and Z=-2380..-2300. All 493
rows of the actual 454-column map were rebuilt in an isolated test identity.

The old contour bisection made hairline triangles and competing curb strips when
an inclusive brush boundary landed exactly on a grid corner. The existing roads
did not use those new brush partitions. The new regression fails on the old code
and passes after exact-endpoint handling and collapsed-face removal. The actual
saved map produces zero slivers at the new road's boundary. Elevation, curve,
preparation and terrain-persistence checks pass. Studio views around the affected
road, including a shallow camera angle, show clean curb edges.

Derived terrain generation 11 invalidates old cooked geometry while preserving
authored roads and the saved document format. No global height or depth-bias
adjustment was made. The three shop labels were inspected on the Neris minimap.

## Ownership and growth

The contour algorithm remains in `SurfaceContours3D` (+21 physical lines); its
regression stays in `TownElevationTests` (+8). `TownDocumentMap` gains three label
conditions. Cache generation replacements have zero net source-line growth.
The existing `TownArmoryRoom` adds three lines for pedestal clearance. Asset
preparation adds seven lines to source the new room independently of the keeper.

The new authoring sources contain 245/162/155/206 physical lines in
`build.py`/`furnishings.py`/`geometry.py`/`export_runtime.py`. They own shell and
review setup, furnishings, mesh/material helpers, and native export respectively.
Existing shared Studio visit, party, camera, collision, and panel owners remain
authoritative. Game code delegates to them; no parallel game implementation,
renderer/compiler change, new dependency, guardrail exception, or entry-point
feature algorithm was introduced. Architecture notes in both repositories identify
the new canonical room package separately from Garran's character package.

## Limits and evidence

The Blender master retains the complete shell and detailed trim. The game uses
the roof/entrance cutaway, simplified small bevels, flat lettering and baked color
variation. It omits procedural micro-bump. The runtime export checks engine vertex
and part limits, removes collapsed lettering triangles, and repairs unusable
tangents only for isotropic materials without normal maps. No engine validation
threshold was relaxed. Keep the vertex-limit check when adding more detail.

Visual review covers the observed views, not every possible road layout or camera.
Weapon purchases retain the existing session-only demonstration behavior.

Local logs: `artifacts/neris-road-flicker-20261008` (baseline, fixed, actual-map,
asset, Studio and game build checks) and
`artifacts/armory-check-49b3d4433ecc41a4895f56d60d5e7ae8` (46 native checks).
Studio was gracefully replaced with the verified build; no unsaved authoring
session was force-terminated. No .NET or VSIX rebuild is required. The native
executables were already rebuilt; browser refresh is not involved.

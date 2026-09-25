# Neris Buildings — Design Set 1

Eight building contact sheets for Sin Star I, created September 25, 2026 using the built-in image generation tool.

## Contact sheets

Each PNG is **1254 × 1254 pixels** and contains four labeled elevations:

| Top left | Top right |
| --- | --- |
| Front | Back |
| **Bottom left: Left** | **Bottom right: Right** |

1. [Weapon Shop](../../asset/images/neris-buildings-v1/01-weapon-shop.png) — 10 × 8 × 9 m
2. [Armor Shop](../../asset/images/neris-buildings-v1/02-armor-shop.png) — 12 × 9 × 8 m
3. [Items Shop](../../asset/images/neris-buildings-v1/03-items-shop.png) — 8 × 8 × 9 m
4. [Communication Tower](../../asset/images/neris-buildings-v1/04-communication-tower.png) — 7 × 7 × 24 m
5. [Town Hall / City Center](../../asset/images/neris-buildings-v1/05-town-hall.png) — 34 × 22 × 24 m
6. [Home 1 — Modest Cottage](../../asset/images/neris-buildings-v1/06-home-cottage.png) — 7 × 6 × 6 m
7. [Home 2 — Family House](../../asset/images/neris-buildings-v1/07-home-family.png) — 11 × 8 × 9 m
8. [Home 3 — Roundhouse](../../asset/images/neris-buildings-v1/08-home-roundhouse.png) — 8 m across × 10 m high

Dimensions are suggested modeling targets (width × depth × height), not measurements encoded in the images. The town hall is intended to be much larger than the shops and homes; separate sheets are framed to fit, not shown at a shared scale.

## Design direction

Warm ivory limestone and cream plaster, deep blue roofs, restrained aged brass/gold trim, arched openings, and star details connect these buildings to the existing Neris market and palace artwork. Shops have sword, breastplate, and flask emblems. The tower adds a cyan relay crystal. Residential silhouettes vary between gabled cottage, broad family house, and octagonal home.

The 2×2 sheets are concept references for reconstruction. Small architectural details may differ between generated elevations; reconcile these during modeling. No Tripo3D conversion or import has been performed. No Blender models are included: Blender's MCP server was unavailable during this task, and its unsaved scene was preserved.

## Authoring and validation

- [Exact generation prompts](prompts.json): concatenate `common_prompt` and each building's `spec`.
- [File manifest](manifest.json): dimensions, sizes, SHA-256 hashes, and view order.
- All eight sheets were visually reviewed and all eight PNG files passed decoding/integrity checks.
- Saved deliverables: `../../asset/images/neris-buildings-v1/`.
- These are new image assets; no application code changed. No .NET compilation or application restart is required.

Created by: Louiery R. Sincioco (Sin).

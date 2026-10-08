# Neris weapon shop V2

The rebuilt room follows Neris's established ivory stone, teal enamel, brass,
arched displays and cyan crystals. It has a continuous polished floor, a central
Dawnstar sword display, fitted weapon cabinets, a sales counter, and an armorer's
workbench. No image or UV tile is repeated across the floor or walls.

## Open and rotate

Open `Neris-Weapon-Shop-V2.blend` in the installed Blender 5.2. The model contains
all four walls, the entrance and a complete dome, plus individually editable
furnishings. No external texture downloads are needed.

- Middle mouse drag: orbit freely through 360 degrees.
- Wheel: zoom. Shift + middle mouse: pan.
- Numpad 4/6: orbit in 15-degree steps; Numpad 2/8: change elevation.
- The top-right View Layer selector offers `Complete shop`,
  `Interior - roof and entrance removed`, and `360 - all walls removed`.

The latter two are review cutaways of the complete model. The full shell uses
Neris's architectural vocabulary; it does not replace the existing outdoor
weapon-store building in the authored town.

## Studio and game asset

`Armory-Room.glb` is the twelve-material, thirteen-part, 49,769-triangle runtime
cutaway (130,261 exported vertices, within the engine's 131,072 limit).
`room.sm3d.json` and `runtime-report.json` describe the export. The five unique
baked atlases preserve the spatial color variation of the procedural authoring
materials. Blender's fine procedural bump is omitted from the runtime export;
physical bevels remain modeled with fewer segments, and small lettering is flat.
The editable Blender master retains the detailed curved trim and raised letters.
All textures are embedded in the GLB.

Studio's existing `Prepare-BuildAssets.ps1` copies this package to its armory
build inputs. The game reuses those inputs and the same `TownArmoryRoom` owner.
The keeper, party presentation, conversations and purchases retain their existing
owners. The floor is grounded at zero; native model scale remains 1000 percent.
The central pedestal reserves a 1.45 m radius for the leader's movement.

## Authoring ownership

- `Source/geometry.py`: mesh helpers and nonrepeating material finishes.
- `Source/furnishings.py`: weapon displays, counter and workshop.
- `Source/build.py`: room shell, collection layout, review views and renders.
- `Source/export_runtime.py`: evaluated geometry, unique atlas baking, native
  material grouping, triangulation and export checks.

Rebuild only in a fresh background Blender process with `--factory-startup
--python Source/build.py`. This regenerates the canonical model and previews;
save any manual model revisions separately first. Run `Source/export_runtime.py`
in background Blender after model edits to refresh the GLB. It reads the saved
model and does not overwrite that model or any live Blender session.

## Validation

The complete shell and both cutaways were inspected in Blender, including a
24-step full orbit. Four render previews are under `Previews`. The export drops
zero-area font-bevel triangles before native cooking; no renderer tolerance or
asset-validation rule was relaxed. Final native acceptance and shared road-fix
evidence are recorded in `VALIDATION.md`.

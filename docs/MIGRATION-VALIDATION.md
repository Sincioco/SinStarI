# October 4, 2026 migration verification

The native game moved from `D:\SMILE 2.0\games\SinStarI` to this repository's
root. The old physical directory was sent to the Windows Recycle Bin after build
and runtime validation. Its former path is now an ignored directory junction to
the canonical checkout. Visual Studio opened the solution from the new location.

## Preservation

- All 2,241 files in `Visual Script and Storyboard` retained their paths, lengths,
  and last-write timestamps; no files were added there.
- The copy inventory found no missing files among 4,018 non-cache source/input
  files. Build preparation refreshed the expected Arin and Orin calibration assets.
- SHA-256 matched all 2,893 unchanged source-asset files. Three native preparation
  scripts have intentional relative-path updates for their new root.
- The game subdirectory's 173 commits were retained through a filtered-history
  merge. Filtering changed commit identities and excluded videos; it did not
  rewrite either repository's existing published branch.
- No video files are included in the new Git index. Local copies remain available.

## Executed checks

- Native Release build from the independent root: 277 source files and 916
  published assets, using the existing local compiler and toolchain.
- Map acceptance: **104 assertions passed**, covering the unloaded-thumbnail
  regression, all 17 map packages, four-member loading, movement, day/night
  photography, and idle selection preservation.
- Battle rules: passed.
- Battle presentation/capture: all three bosses loaded and produced the 12
  requested hero-action photographs, including Orin's Thor Attack and Mira's
  Heal Party. The fixture samples genuine shared-renderer frames.
- Targeted SMILE style check: all nine changed/new source targets passed.
- README: all 55 local links resolve; 34 town and 12 battle images are present.
- Interactive native checks: title ordering, both thumbnail pages, opening maps,
  and the shared exploration/camera controls.

## Ownership and growth review

`Program.smile` remains lifecycle/routing code at 141 lines (net +11).
`TitleScreen.smile` is 409 lines (net +7). New map owners are 86 lines for asset
records, 125 for catalog preparation, 219 for the browser, and 109 for exploration.
The shared town scene gained nine net lines and its document session gained 41
for the play-host boundary and idle behavior. Project XML grew to declare shared
sources and assets; it contains no feature algorithms.

Rendering, party simulation, collision, document state and camera behavior remain
with their established Studio owners. No compiler extension, dependency cycle,
third-party installation, size-baseline override or repository-wide refactor was
introduced. There is no automated architecture gate in this game repository;
coupling and source growth were reviewed manually.

## Limits

This verifies the native Windows development setup. Web remains on hold. The
game still needs the sibling SMILE 2.0 toolchain and existing licensed/private
local authoring inputs. It is not a dependency-free fresh-clone distribution.
The existing large shared Studio modules remain architectural debt. The original
Studio session was preserved; these game-only host options retain Studio defaults.

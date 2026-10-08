# Approved illustrations and narration

Sin approved these 10 existing images after reviewing the proposed placements. The original novel HTML is the placement source and embeds the optimized WebPs. `illustrations.json` records each approved source, checksum, insertion paragraph, stable block ID, dimensions and descriptive alt text. Storyboard originals and the Markdown manuscript remain unchanged.

| Chapter | Storyboard source | Insert after block |
| --- | --- | --- |
| ch-01 | `panel-01-1.png` | `ch-01-b0005` |
| ch-04 | `c01-s01-carry.png` | `ch-04-b0043` |
| ch-09 | `panel-03-2.png` | `ch-09-b0045` |
| ch-14 | `c04-s02-added.png` | `ch-14-b0023` |
| ch-19 | `c05-s01-added.png` | `ch-19-b0005` |
| ch-21 | `panel-07-3.png` | `ch-21-b0048` |
| ch-25 | `panel-08-4.png` | `ch-25-b0059` |
| ch-34 | `panel-11-2.png` | `ch-34-b0007` |
| ch-36 | `c09-s01-added.png` | `ch-36-b0017` |
| ch-41 | `e01-s01-added.png` | `ch-41-b0068` |

`ch-41` is the epilogue; its image follows the last narrative paragraph and precedes The End. Reveal illustrations stay inside their chapters. The images have no visible captions or additional narrated text.

## Build and cache ownership

`build_site.py` reads the original novel HTML. `illustrations.py` verifies each embedded image against its approved checksum, exports the WebP to the web `images/` folder and writes `storyboards.json`. Rebuilds reuse the single source figure rather than adding another one. The annotation parser excludes figure content from narration and paragraph numbering. Do not hand-edit the web-only image placement; change the original source and approved record together if Sin requests a different placement.

`book.json` owns the unchanged audio and timed cues. A cue matches exact `data-cue-id` values and normalized words plus their hash, independently of DOM positions. Preserve existing paragraphs, spans, text and IDs. A caption must never receive a cue ID.

Figures use `data-no-narration="true"`, stable illustration IDs, descriptive alt text, lazy loading and asynchronous decoding. Intrinsic width/height reserve space; responsive CSS keeps the complete image within the reading column without cropping. The existing ResizeObserver rechecks following after layout changes. Figure clicks do not seek or start playback.

`refresh_cache.py` hashes the shell and every explicit image in `storyboards.json`. The 10 WebPs add 1,575,256 bytes to offline page storage, separate from the 72,303,282 audio bytes shown in the download UI. The builder keeps the previous audio-cache version when the manuscript, media and cues are unchanged, so image updates do not discard downloaded audio or saved listening position.

Run `python production/build_site.py` to rebuild from the embedded source, or `python production/refresh_cache.py` after presentation-only edits. Authoring files under `production/` are not deployment assets. Include `images/` and `storyboards.json` when the parent coordinates deployment.

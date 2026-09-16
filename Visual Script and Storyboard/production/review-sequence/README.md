# Story Video Sequence Review

Double-click **Render Review Movie.cmd** in the website folder. The small Windows
window lets you edit/select a JSON sequence, render, follow progress, cancel, and
play the finished movie. Closing the window leaves the background render running;
opening it again shows the current progress. The renderer never uploads files.

The delivered output is `asset/videos/Sin-Star-I-Story-Video-Sequence-Review.mp4`.
The default review contains every one of the 135 website preview clips: a
two-second still poster, animated poster, story scenes in Storyboard order,
alternate takes immediately beside their original, optional scenes, seven cast
animations, and 18 seconds of illustrated credits. Existing edited films are not
duplicated inside the review. The complete frame is preserved with letterboxing.

## Play and review immediately

Double-click **Play Sequence.cmd**, or select **Play Sequence** in the Windows
renderer window. Open `http://localhost:8765/review.html` to use the running server.
No movie render is needed: the player reads the same JSON and plays source clips
directly. **Spacebar** pauses/resumes, except while typing or using input controls.
Clicking the video also pauses/resumes the clip and music in either playback mode
or full screen. Clicking the scene panels or their arrows keeps playback running.
Previous, Next, the clip picker and seek bar let you review any moment.

| Key | Action |
| --- | --- |
| Spacebar | Pause / resume |
| Home | First video clip |
| Left Arrow | Previous video clip |
| Right Arrow | Next video clip |
| Up Arrow | Toggle Panels Over Video / Video Left · Panels Right |
| Down Arrow | Enter / exit full screen |
| End | Last video clip |

Navigation preserves paused/playing state. Home/End and Left/Right target videos;
the opening still and ending credits remain in automatic playback and the picker.
Up Arrow preserves the current clip and playback position and saves the selected
layout through the same automatic JSON workflow as the Playback Mode selector.
Shortcuts do not override text fields, sliders, checkboxes, selects, or modified
browser shortcuts. Holding a key does not repeatedly skip clips.

- **Panels Over Video**: hover over either panel to reveal four corner arrows.
  Keyboard focus also reveals them; touch devices show them continuously.
  You may move panels during playback or while paused. Each clip remembers its
  own positions. Choosing the other panel's corner swaps the two positions.
- **Video Left · Panels Right**: the full video stays on the left. Scene Information
  appears above Scene Context on the right. Detailed story notes remain visible
  while playing, and long notes scroll. Overlay positions are retained when you
  switch back. The MP4 uses the same column arrangement with text fitted to its frame.
- **Mute This Clip**: mutes only that clip's original audio. Background music keeps
  playing. Each alternate take has its own mute and position preferences.
- **Show Labels** and the three volume sliders apply to the whole sequence.
- Purpose, character development, revelations and later connections are editorial
  notes in `scene_notes`, keyed by scene ID. Spoilers are intentional. Full notes
  appear when an overlay is paused and throughout side-by-side playback; the
  overlay movie uses the compact purpose/context panels to preserve more picture.

The local server automatically writes changes to the selected JSON inside
`production/review-sequence`. Wait for **Saved for the MP4** before starting a render.
Settings survive refresh/reopening and apply to the next MP4 render. **Save JSON**
also downloads a portable copy. An already rendered MP4 does not change until you
render again. The renderer snapshots settings at startup and reports newer edits
made while it was working.

If automatic saving is unavailable, the page keeps changes in browser storage
and clearly asks you to **Save JSON**. Replace/select that downloaded configuration
in the renderer. Files opened through **Open JSON** use this download workflow;
the browser does not silently overwrite an arbitrary selected file. Music continues
from its current place when you jump between clips in live review; a full render
always follows the configured music sequence from its beginning.

### Layout and per-clip settings in JSON

```json
"settings": { "fps": 24, "encoder": "auto", "panel_opacity": 0.8,
              "layout": "side-by-side", "show_labels": true },
"panel_positions": { "scene_info": "lower-left", "scene_context": "lower-right" }
```

Use `"overlay"` or `"side-by-side"` for layout. Within an individual clip object:

```json
"muted": true,
"panel_positions": { "scene_info": "lower-left", "scene_context": "lower-right" }
```

Omitted clip settings inherit the global panel positions and keep original audio
enabled. All four corner names are supported. The two panels must use different
corners. Muting clip audio does not mute the background music.

After a global panel reset, `panel_layout_version` invalidates older cached panel
positions and rejects position saves from tabs that predate the reset. Refresh
Video Clips before making new placements. Audio and other review preferences are
preserved, and new per-clip placements can be saved normally.

## Volume controls

Edit `sequence.json` and render again:

```json
"audio": {
  "clip_volume": 1.0,
  "music_volume": 0.18,
  "master_volume": 1.0
}
```

- `clip_volume`: original clip dialogue, ambience and effects.
- `music_volume`: the three supplied background music tracks.
- `master_volume`: the combined final soundtrack.
- `0.0` means mute, `0.5` means half the signal amplitude, `1.0` means normal,
  and `2.0` is the maximum boost. Perceived loudness is not a linear percentage.
- The default keeps original audio at normal level and music quieter. Set
  `clip_volume` to `0.0` for music only, or `music_volume` to `0.0` for clip audio only.
- A final peak limiter prevents overload when sounds overlap. Volume-only edits
  reuse the cached video segments; they do not re-encode all the pictures.

Music plays in this repeating order: **Starforge Horizon → Starforge March → Bloom**.
The default overlap is two seconds, including the return from Bloom to Horizon.
There is no inserted silence between tracks. Only the ending fades fully to silence.

## Edit the sequence

The `clips` array is the playback order. Move an object to reorder it; duplicate
an object with a new `id` and `file` to add a clip. All paths are relative to the
website folder. Original media is never modified.

Each clip has `id`, `enabled`, `file`, `chapter`, `scene`, `scene_title`, `context`
and an optional `take` label. Set `enabled` to `false` to omit a clip. Filenames
are displayed automatically. Chapter, scene and filename appear together at the
lower left by default; context appears at the lower right. Saved per-clip positions
override these defaults. Panels default to 80% opacity.
You may use `\n` inside `context` for a paragraph break. Long labels wrap; an
oversized panel stops preparation with a specific message instead of hiding text.

Optional `start_seconds` and `duration_seconds` trim an entry. Omitting both plays
the whole source. The default 1920×1080 output preserves the full source frame at
24 fps; `settings.fps` may be changed. `settings.encoder` is `auto`, `h264_nvenc`
or `libx264`. Auto uses installed NVIDIA encoding when available and otherwise
uses the installed CPU encoder. No encoders or packages are downloaded.

`opening`, `credits`, and `music` control the title image/duration, credit artwork,
text/links/duration, music files and crossfade. Keep credit text within the designed
panel. The first-game statement and creator line are editable text, not baked
into the source artwork.

## Files and reuse

- `sequence.json`: editable source of truth; no website rebuild rewrites it.
- `sequence-timeline.csv`: generated start/end times and exact source filenames.
- `sequence-render.json`: completed output checksum, timing, audio settings and
  music transition positions.
- `render_review.py`: validates inputs, orders the segments and assembles the film.
- `review_art.py`: text layout and illustrated credits.
- `review_media.py`: FFmpeg execution, probing and progress.
- `Review-Movie.ps1`: responsive Windows controls and background process launch.
- `Save-ReviewSettings.ps1`: narrow local HTTP write handler for review preferences;
  it preserves story text, media paths and sequence order.
- `../../asset/sequence-player.js`: playback, labels, navigation and keyboard controls.
- `../../asset/sequence-settings.js`: per-clip preferences, recovery and automatic saves.
- `../../asset/sequence-audio.js`: clip gain, music gain, master gain and live crossfades.

Runtime tools are the already installed Python/Pillow, FFmpeg/FFprobe and PowerShell 7.
The launcher finds the installed Codex Python runtime first, then Python on PATH.
No new dependencies are installed. A different computer needs those tools present.

For command-line use, run from the website folder:

```text
python production/review-sequence/render_review.py
python production/review-sequence/render_review.py --config production/review-sequence/sequence.json
python production/review-sequence/render_review.py --prepare-only
```

`--prepare-only` checks files, prepares labels/credits and writes the timeline.
All temporary overlays, audio, logs and reusable encoded segments live in the
Git-ignored `production/local-state/review-sequence` folder. Cache keys include
source and overlay hashes, timing, frame rate and encoder. Unchanged segments are
reused; the finished output is replaced only after the new file passes its timing
check. Cancel leaves the last completed movie intact. A lock prevents concurrent
renders from overwriting one another; after an abnormal process crash, confirm
the PID in `render.lock` has exited before removing that stale lock.

Every video and every intermediate render remains excluded from Git. The three
user-supplied MP3s, original credit background, canonical SMILE logo, settings,
program and timing records stay with the website for reuse.

## Validation — September 16, 2026

- `check-player.cjs` executes isolated playback interactions: Spacebar, movement
  during playback, per-clip position/mute isolation, corner swaps, automatic save,
  reopen, JSON export and recovery when the local write endpoint is unavailable.
- The local HTTP save handler was exercised against a temporary configuration;
  selected settings reached disk, unrelated clip data stayed intact and a
  cross-origin write was rejected. The temporary configuration was removed.
- All 135 side-by-side note layouts fit. A seven-second rendered sample placed
  video on the left and notes on the right. Its muted clip measured digital silence
  (-91 dB in FFmpeg's 16-bit volume check); the next clip retained its original audio.
- The complete movie passes `validate_review.py`, including config/output checksums,
  16,360 frames, 137 chapters, exact sequence order, audio continuity and the Windows
  progress-file sharing regression. Full FFmpeg decoding reports no errors.
- Static site checks preserve script/canon text, check all four pages and local
  references, and validate JavaScript syntax. Existing hover behavior checks pass.
- Movie sample frames were inspected. Browser visual/interaction testing was not
  performed; the live page is ready for the user's testing.

Run the focused checks from the website folder:

```text
node production/review-sequence/check-player.cjs
pwsh -NoProfile -File production/review-sequence/check-settings.ps1
python production/review-sequence/validate_review.py
python production/validate_draft3.py --require-videos
```

The HTTP settings check requires the local website server to be running. After
editing the sequence settings, render again before validating the movie receipt.

No new packages or architecture exceptions were introduced. The renderer remains
under 260 lines; art, media operations, native controls, player state, audio and
settings persistence have focused owners. No .NET build is required. Refresh the
browser with Ctrl+F5 after updates; JavaScript and styles use content versions.

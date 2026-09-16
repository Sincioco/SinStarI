# Draft 3 Production

## Current local workflow

The continuous **Story Video Sequence Review** is built with
[`review-sequence/sequence.json`](review-sequence/sequence.json) and the
[review renderer](review-sequence/README.md). Its JSON owns playback order, labels,
credits, track order and independent clip/music/master volumes. Start it with
`Render Review Movie.cmd`; it renders in the background and displays progress.
`Play Sequence.cmd` opens the immediate player at `review.html`. It supports
Spacebar pause/resume, video-left side-by-side notes, hover corner arrows and
per-clip mute/position settings. The local server saves preferences into the JSON
for subsequent renders. Playback, preference persistence and audio have separate
owners in `asset/sequence-player.js`, `sequence-settings.js` and `sequence-audio.js`.

The canonical editable website is now `D:\SMILE 2.0 - Sin Star I\Visual Script and Storyboard`,
in the independent public [SinStarI repository](https://github.com/Sincioco/SinStarI).
Make HTML, CSS and JavaScript changes directly in this folder. Do not generate
routine ZIP exports or update the old SMILE-2.0 storyboard copies.

`build_draft3.py` is a full reconstruction from the archived `source-pages` inputs.
**Do not run it after direct narrative/layout edits without first reconciling those
edits with its inputs.** Ordinary YouTube-record updates use `youtube_catalog.py`;
it updates only the playback map and its cache version, preserving authored HTML.
After direct asset edits, `python production/refresh_versions.py` refreshes cache
versions without reconstructing the pages.

All 130 original hover MP4s were renamed without changing their bytes. See
`video-renames.json` for the old/new paths and checksums. Preserve stable media IDs
when changing filenames so remembered selections continue to work. Five additional
planet-throw takes and the two new dream-duel clips bring the total to 137. For the planet
throw, Clips 1 and 2 remain available; Clip 3 is the initial choice when a user
has not remembered another take.

The [concealed-opponent duel and giant-Kael variation](C00-S01-Duel.md) now play before
`C00-S01 - Wide - Unreachable.mp4` in the review and has matching Script and
Storyboard figures. New LTX jobs default to exact 16:9 at 1024 × 576; previews
export at 960 × 540. Earlier accepted clips retain their original framing.

Videos, including intermediate render sources, must never enter Git. The root
`.gitignore` covers common video formats regardless of folder and filename case.
The three previously uploaded complete films are reused, not uploaded again.

## YouTube records and playback

Current checkpoint: **104 of 141 videos have verified links**. The earlier daily
upload limit left 35 pending; the two new duel clips bring that total to 37. Follow
[YouTube-Upload-Checkpoint.md](YouTube-Upload-Checkpoint.md) to resume without duplicates.

- `youtube-uploads.json` owns upload status, exact local file checksum, title,
  YouTube ID, visibility and verification time. Never mark an upload complete from
  a submitted file alone: confirm its Unlisted save in YouTube Studio.
- `youtube_catalog.py --stage 15` prepares a local batch of hard links for the
  browser file chooser; it performs no network uploads. Staging is Git-ignored.
- Upload through the signed-in in-app browser, with Chrome only after an in-app
  failure. Keep new clips Unlisted, ads off, and include the required credits.
- After verified UI completion, use `youtube_catalog.py --record CLIP_ID YOUTUBE_ID`.
  This regenerates `asset/youtube-uploads.js` and versions that asset in the HTML.
- `asset/animated-pictures.js` owns preview state, variations, local fallback and
  player lifetime. `asset/youtube-preview.js` is the small lazy IFrame API adapter.
  Missing media logs to the console; it does not put failure messages over artwork.
- `serve.ps1` and the Start/Stop Website launchers provide local HTTP using installed
  Windows/.NET components and PowerShell. They support byte ranges for video seeking,
  prevent stale cached pages and send a normal cross-origin referrer for YouTube.

YouTube's [client identity requirements](https://developers.google.com/youtube/terms/required-minimum-functionality#embedded-player-api-client-identity)
require an HTTP referrer. A browser's `file://` page cannot provide one reliably;
use the launcher for embeds. Direct file viewing keeps illustrations, local clips
and external YouTube links working. Audio autoplay may require a user click.

## Self-contained authoring materials

`references` contains copied source artwork and the supplied poster/character
references. `templates` contains the LTX 2.5 API and UI workflow templates.
`render-sources` preserves reused movie excerpts; `renders/clips` preserves original
animation outputs, with matching `renders/history` receipts. `source-materials.json`
records their provenance. Render videos remain local and ignored by Git.
`briefs` preserves the local-organization request. ComfyUI's installed models and
its input/output endpoints remain external tools; no software was installed.

## Current validation commands

```text
python production/validate_draft3.py --require-videos
python production/validate_media.py
node production/check-preview-behavior.cjs
```

Omit `--require-videos` when validating a video-free Git clone. The current checks
do not require the earlier drafts to be sibling folders. `baseline` retains the
pre-organization edition for narrative comparison. Historical results below and in
`Validation.md` describe earlier editions, not browser acceptance of the new embeds.

## Earlier Draft 3 production history

The delivered HTML works directly from disk without production tools, a server,
external fonts, package downloads or an internet connection.

## Ownership

- `build_draft3.py` adds poster, cast figures and preview wrappers to the preserved
  Draft 2 HTML in `source-pages`. It leaves narrative text untouched.
- `site_shell.py` owns the shared header and 53-scene sidebar. It replaces the two
  old navigation shells and permits packaged styles, scripts and videos in the
  Full Script's content security policy.
- `asset/site-theme.js` applies the theme before painting. `asset/site-shell.js`
  owns the theme preference, scene search, current-scene links and print action.
  `asset/site-shell.css` owns the shared shell and both palettes.
- `asset/animated-pictures.js` owns the single active preview and its lifecycle.
  It cancels stale play requests, unloads departed clips, pauses hidden/offscreen
  media, respects reduced motion and supports touch/keyboard activation.
  Its companion stylesheet owns video overlays and controls.
- `asset/media-preferences.js` owns shared audio and remembered clip choices.
  It persists them in local storage and carries them in local view URLs when
  file storage is restricted. Clip controls use the same picture IDs in both views.
- `hover-media.json` maps all 129 pictures to preview, source, provenance and edits.
  Optional `variants` add clips; `default_clip` selects the starting take when no
  preference is saved. `media_catalog.py` expands this inventory for queueing,
  collection, HTML generation and validation. There are currently 130 clips.
  `cast-portraits.json` records the seven new portraits.
- `queue_hover.py` appends missing LTX 2.5 jobs to the existing local queue.
  `collect_hover.py` collects jobs and exports H.264/AAC previews with original audio.
  `validate_media.py` fully decodes new or changed clips once.
- `validate_draft3.py` validates links, exact image/video pairings, shared navigation,
  script text, cast/poster placement, security policy, JavaScript syntax and hashes
  of both earlier drafts. `html_document.py` supplies its small HTML inventory.

## Media decisions

The edition reuses 45 existing LTX renders: the 44-shot film selection, with its
reviewed second takes, and the armorer shot from Room for One. Existing edited
movie framing removes generated lettering where needed. The lower authored caption
band is cropped out for hover use. Seven reviewed clips retain full framing
to protect foreground characters; two of these use shorter clean excerpts.
Wider previews are contained within the original illustration area without stretching
or clipping additional faces. Each source and edit is recorded in the media map.

Another 84 pictures have new animation: 76 story illustrations, the supplied
poster and seven new action portraits. Ordinary clips use 97 frames at 24 fps with
restrained image-conditioned motion. The additional Aevos planet-throw illustration
in C09-S03 has a dedicated eight-second, 193-frame action sequence. Its new caption
and dialogue accompany the figure; all previously accepted script prose is preserved.
Saved API/UI workflow pairs record LTX 2.5
distilled 22B INT8, existing local encoders/VAEs/upscaler, fixed seeds, and full
initial-image conditioning. No models or packages were installed.

The planet-throw scene also has a revised take that keeps Mira's head and body
aligned through the impact. Clip 1 retains the original picture sequence; Clip 2
is the new default. Both use the same illustration and remain selectable.

All 130 previews now include audio. The carry-together scene uses the original
LTX audio because its edited-film intermediate was silent; `audio_source` records
that correction. Other clips retain their selected source soundtracks. First-visit
audio is off; one header click enables it. A rejected sound autoplay request falls
back to muted video with an explicit Play With Sound action. See the official
[Chrome autoplay policy](https://developer.chrome.com/blog/autoplay/) for the
browser interaction requirement. Muting stops sound immediately without reloading.

The original poster title remains visible over the top portion of its animation,
so its lettering stays exact. Static artwork remains underneath each preview,
including while media loads or if playback is unavailable.

The Orin/father hover excerpt ends before an unwanted generated embrace. The first
2.5 seconds of `new-c01-s04` take 2 keep Arin's sword lowered during the quiet conversation.
First takes and original movie files remain untouched.

## Rebuild and validate

With the existing Python/Pillow installation, run:

```text
python production/queue_hover.py
python production/collect_hover.py
python production/build_draft3.py
python production/validate_draft3.py
python production/validate_media.py
```

Queueing is needed only for missing renders. Receipts prevent duplicate submissions.
Use `collect_hover.py --refresh-all` to re-export existing clips after export changes.
Collection reads `http://127.0.0.1:8191` and retains original renders in the separate
`Sin Star I - Draft 3 Animations` output folder. Saved workflows also open in ComfyUI.

Use the general bundled Python runtime for production scripts. The isolated
ComfyUI interpreter is not required to view or rebuild the pages. Existing FFmpeg
and Node installations are used for media export/validation and syntax checks.
No application build is required.

Sibling Drafts 1 and 2 are needed only for preservation validation. HTML rebuilds
use this edition's included baseline `source-pages`; those files are production
inputs, not additional website entrypoints.

## Validation scope

See `site-validation.json`, `media-validation.json`, `render-status.json` and
`Validation.md` for final evidence. Isolated behavior checks exercise playback,
reduced motion, theme transfer, navigation and search; they are not a browser
visual test. The ComfyUI queue was checked in the user's existing Chrome tab.

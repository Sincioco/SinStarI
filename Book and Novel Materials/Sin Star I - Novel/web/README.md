# Sin Star — Book One: web reader

## Music and personal bookmarks (October 8, 2026)

The bookmark icon sits immediately after Chapters. Select text, open Bookmarks,
add an optional note, then choose Bookmark selection. Saved items show the exact
quote, chapter and note; notes can be edited and deletion requires confirmation.
Open & listen resolves the original block offsets and cue ID/hash before seeking.
Changed quotes, missing blocks, and untimed title text never invent a timestamp.
Bookmarks use local browser storage only; denied storage is explicitly session-only.
The bookmark highlight uses a separate CSS Highlight (or block outline fallback),
leaving narration's yellow cue highlight and the manuscript DOM intact.

Background music cycles Starforge Horizon (Title Screen), Starforge March (Orin),
then Bloom (Arin). The bottom-right music-note button opens a dismissible modal panel. It keeps
the original compact player height (178px desktop / 199px phone), with no extra
control rows. Music starts at 8% when no preference is saved and retains an
existing volume/mute choice. The single-note icon has a 34×28px visual border,
matching A−/A+, inside its retained 44px touch area. The close button, Escape and
focus return work with keyboard and touch. Enable music now confirms readiness
while narration is paused, shows Music playing during playback, and clears mute
or restores 8% from zero volume when explicitly pressed. One Web Audio context and GainNode play music independently
of narration's media element. Playback gestures create/resume the context directly;
Enable music retries after browser interruption. Narration pause, buffering, error,
chapter source changes and ending stop music, preserving its current track/offset.
At most the current and next decoded tracks are retained. Missing music never
prevents narration. Autoplay remains subject to browser permission.

The three web MP3s are unchanged copies totaling 11,547,340 bytes. Narration and
original music files are untouched. Offline chapter downloads contain narration
only. Download music is a separate, optional, SHA-256/length-verified download;
its saved count reflects verified Cache Storage copies. Music is not part of the
mandatory service-worker install, and removing it leaves narration caches intact.

`music.js` owns playback/controls; `music-cache.js` owns optional verified storage.
`bookmarks.js` owns UI/storage; `bookmark-anchors.js` owns selection and anchors.
`production/music_assets.py` exports copies and `music.json` on full rebuild;
`build_site.py` owns markup, and `refresh_cache.py` versions the new modules.
The publication updater's explicit allowlist and music hash checks must accompany
these files. The main website wrapper is unchanged.

Validation: `test-follow-default.mjs` (35), `test-startup-bookmarks.mjs` (8),
`test-music.mjs` (12), and `test-bookmark-data.mjs` (4). Browser evidence is in
`features-browser-validation.json` and `features-edge-validation.json`, covering
desktop/390px layout, real decoded MP3 transitions (source duration shortened for
the test), bookmark CRUD/reload/cross-chapter navigation, offline music/narration,
missing music, denied storage, touch selection guards and rapid navigation.
`features-file-validation.json` confirms 43 unchanged narration hashes, 3,048
unchanged cues, 43 exact unchanged narrative sections, 10 unchanged illustrations,
original music checksums, retained audio cache identity and repeatable rebuilds.
Physical iPhone/Chrome/WebKit and subjective listening remain unverified.

`music-panel-validation.json` compares the player against the pre-music stylesheet
at 1280px desktop, 390px and 320px phones, and 844px landscape. The player remains
178px on desktop and landscape, and 199px on phones, both with the dialog open and
closed. It also checks the 44px music button, keyboard opening, slider adjustment,
close/Escape focus return, and preservation of an existing volume/mute preference.

The implementation follows [WebKit's gesture requirements](https://webkit.org/blog/6784/new-video-policies-for-ios/)
and [Chrome's AudioContext resume guidance](https://developer.chrome.com/blog/autoplay/).
Independent gain follows the [Web Audio GainNode specification](https://www.w3.org/TR/webaudio/#GainNode),
avoiding reliance on an iOS media element's volume setter. These policies do not
guarantee background playback or autoplay inside the deployed cross-origin iframe.

Deployment-ready static website, built from the original novel HTML. **42 chapters plus the new title introduction**, with the accepted Michael/Bella/Uncle_Fu/Aiden performance. Audio is the approved mono 32 kbps mobile edition; the title introduction uses Michael at speed 0.97 and says exactly **“Sin Star. Book One. Created by Sin.”** Audio totals **72,303,282 bytes** (72.3 MB). No synthesis happens in the browser.

## Preview and deployment

For local preview, serve this folder with an existing Python installation:

On this Windows desktop, use `production/Start-Preview.ps1` for the persistent
preview at `http://127.0.0.1:8897/`. It serves the local publication `docs` folder,
verifies the document root, and reuses an already healthy preview. The hidden
Python process is created by Windows management services, outside the Codex task's
process lifetime; it makes no startup entry or scheduled task. Use
`production/Stop-Preview.ps1` to stop only that identified reader process. It also
supports native MP3 byte ranges. Neither launcher changes browser storage.

The earlier command-scoped preview could disappear when the task ended. When it
was stopped, the service worker correctly displayed an older cached shell and
returned 503 for uncached narration. A hard refresh cannot repair a stopped
origin. Start the preview first, confirm `/__preview_health` reports the intended
root, then reload the existing tab; do not clear bookmarks or downloaded audio.

For a temporary foreground preview (keep the terminal running):

```sh
python -m http.server 8894 --bind 127.0.0.1
```

Open `http://127.0.0.1:8894/`. The current desktop preview is served from the parent directory at `http://127.0.0.1:8894/web/`. Opening `index.html` as a file URL does not support module loading/offline storage. No .NET build is required.

Copy these files together to any HTTPS directory on sincioco.com, preserving relative paths: `index.html`, `reader.css`, `app.js`, `cue-navigation.js`, `follow-narration.js`, `offline.js`, `sw.js`, `book.json`, `manifest.webmanifest`, `icon.svg`, `storyboards.json`, and the complete `audio/` and `images/` directories. `production/` and this README are authoring/test records and can stay local. Deployment and hosting account access are separate from the authorized repository commit and push.

The server must serve JavaScript modules with a JavaScript MIME type, MP3 as `audio/mpeg`, WebP as `image/webp`, and JSON as JSON. Keep `sw.js`, HTML and JavaScript revalidating rather than permanently cached. Standard HTTP Range support is useful for streamed audio. All references and the service-worker scope are relative to this folder; no domain, root-path rewrite, external font, CDN, analytics or paid service is required.

## Reading and listening

First visit opens the title page and attempts playback. Browsers commonly block audible autoplay: **Play** starts it when required. Returning visits restore the chapter and timestamp for the same audio/content revision, then attempt playback again. Browser/private-mode storage restrictions are handled without blocking online reading.

Select a chapter to play it. Click or tap an existing narration passage to seek to its recorded start and play. Each chapter has one passage Tab stop; Left/Right Arrow moves between passages, Home/End selects the first/last, and Enter/Space plays. Text-selection drags, links, figures and captions do not seek. Unmatched edited passages cannot redirect playback. `cue-navigation.js` owns pointer/keyboard access; `app.js` retains cue validation and the single audio player. Previous/Next, Play/Pause, seek, font-size controls and keyboard-accessible buttons are provided. Chapter endings advance automatically; the epilogue ends without looping. The controls prevent overlapping audio and discard stale loads after rapid navigation.

Yellow highlighting follows **actual production chunk boundaries** (phrases or paragraphs), not invented word timings. All 3,048 cues were matched against the original text. Small MP3 decoder/encoder timing differences are possible; a long phrase is highlighted as a whole. Pause, seek, cue gaps, errors, changed text and missing cue elements clear old highlights. Headings and title-page text have no invented alignment. Follow narration starts checked on every opening or reload, including when a browser restores an unchecked form state or a page from its back/forward cache. Only explicitly unchecking the checkbox turns Follow off for the current visit. Scrolling, swiping, pinching, wheel and keyboard navigation never uncheck it or suspend following while audio plays. Playback, cue taps and viewport changes respect an explicitly unchecked checkbox. This default does not reset the saved chapter, timestamp or offline audio. Follow narration keeps the first rendered line of an offscreen active passage below the header and above the player, including when the mobile viewport changes. On phone layouts it uses an immediate document scroll. Following continues while a finger is on the reading area. Scroll and gesture events request a position check without changing the checkbox; explicitly checking it again follows the current spoken passage. Reduced-motion preference is respected. `follow-narration.js` owns this viewport and gesture behavior.

The header places the Offline audio icon before the Home icon at the far right. Both have labelled 44-pixel controls and visible keyboard focus. Home opens https://sincioco.com/ as the top-level page, including when this reader is embedded. The icon keeps the existing offline panel and download behavior.

## Offline audio

Open the **Offline audio** download icon in the cream header and choose **Download this chapter** or **Download whole book**. There is no automatic whole-book download. Downloads run sequentially, show progress and support cancellation/retry; completed chapters are kept. Full byte count and SHA-256 are verified before a chapter is marked saved. HTTP 206/truncated files, insufficient quota, cancellation and write failures cannot produce a false completed badge.

Saved browser copies are selected first and played as one bounded chapter Blob at a time. The service worker also handles byte ranges correctly (206/416) for cached audio. Missing chapters fall back to the network; when unavailable, the reader explains that the chapter must be downloaded or the connection restored. Uncached media requests pass through unchanged so the browser’s Range header reaches the server. Saved-offline badges and removal refer only to the explicitly downloaded, verified Cache Storage copies. Removal does not clear browser-managed HTTP/media buffers or interrupt an already playing Blob; a removed chapter is no longer marked saved even if the browser can temporarily replay buffered audio. The page, complete text, controls and cue data are cached for reload offline.

Use **Remove this chapter** or **Remove all offline audio** to reclaim space. Audio revision hashes prevent stale editions from being used. Browsers can evict cache storage; private browsing may restrict it. Check the saved badges before leaving connectivity. This browser storage is separate from Files/Downloads. **Save this MP3 to Files** is a separate ordinary download; the website cannot automatically inspect arbitrary phone files. Keep the page open while downloading; background or closed-tab downloads are not promised.

## Approved novel illustrations

The 10 storyboard illustrations approved by Sin appear in Chapters 1, 4, 9, 14, 19, 21, 25, 34, 36 and the epilogue. They follow the approved passages, with Aevos after his introduction and the bedside scene immediately before The End. They add no narrated captions or spoken text. WebP copies total **1,575,256 bytes**, with original composition preserved and no upscaling.

The original novel HTML owns placement and embeds the optimized images for self-contained reading. `production/illustrations.json` records the approved anchors, alt text, source and optimized checksums. `production/illustrations.py` exports those embedded images to `images/` and writes the explicit offline registry `storyboards.json` during `production/build_site.py`. Rebuilding from the original HTML retains each illustration once. Figures do not receive narration cues or alter paragraph numbering; prose spans retain their IDs.

Run `python production/refresh_cache.py` after presentation edits. It versions the shell and registered images independently of the audio. The full builder also preserves the existing audio-cache identity and saved listening positions when audio, cue timing and manuscript are unchanged. The title-page byline remains **By: Louiery R. Sincioco (Sin)**; the recorded title remains unchanged. For placement and ownership details, see [STORYBOARDS.md](production/STORYBOARDS.md).

## Verification and limits

Run `node production/test-follow-default.mjs` from this folder for 35 focused startup, saved-position, gesture, chapter-transition and viewport regressions. The test runs the actual follow controller, app startup decoder and chapter switcher with simulated DOM/storage/media seams; it does not claim native browser or physical-phone playback. Its report is `production/manual-only-follow-unit-validation.json`. Browser/phone validation of this manual-checkbox-only update remains pending because supported browser controls were unavailable during this edit.

The mobile-follow repair is covered by `production/follow_checks.html` and `production/mobile-follow-validation.json`: phone-width passage positioning, tap drift versus deliberate pan, re-enabling Follow, pause/resume, viewport resizing, chapter navigation, offline playback and timestamp restore. Sixteen geometry/gesture checks also passed. The local server was stopped to confirm cached-shell reload and saved-chapter playback. These checks use desktop Chrome and synthetic touch events; physical iPhone verification remains outstanding.

Chrome desktop and responsive phone viewport checks are recorded in `production/browser-validation.json`. Original rendered prose was compared exactly for all 42 chapters, all 43 MP3 hashes/durations/codecs checked, and title audio fully decoded. Tests cover stable cue matching, inserted image/caption, edited-text failure, pause, resume, navigation races, storage failure, download cancellation/retry, quota, rejected partial response, whole-book download, range seeking, deletion and the final chapter ending. Offline reload/seek/auto-next/missing-chapter checks run with the local HTTP server stopped. `production/browser_checks.html` is the optional local verification fixture; it uses this origin's playback/cache state and is not needed for deployment.

Passage playback checks are in `production/passage_checks.html` and recorded in `production/passage-browser-validation.json`. They cover paused/playing seeks, rapid clicks, source/metadata delays, cross-chapter races, selection, keyboard navigation, invalid text, inserted figures, resume and cached playback. `production/passage-file-validation.json` confirms unchanged narrative sections, all 3,048 cues/timestamps, all 43 audio hashes and the preserved audio cache identity.

Illustration checks are recorded in `production/illustration-file-validation.json` and `production/illustration-browser-validation.json`. They cover exact approved anchors, unchanged prose/cues/audio, repeatable rebuilds, mobile/desktop layout, delayed image loading, follow narration, offline image hashes and retention of a previously downloaded chapter across the shell update. Browser checks use an isolated headless Chrome profile with GPU disabled.

The focused `production/range-browser-validation.json` records native media Range forwarding to the server, seeking an uncached passage, exact cached 206/416 responses and explicit-download removal status, including when browser-managed media buffers may remain.

No physical phone/Safari test or subjective listening claim is made. Autoplay and browser storage remain browser-controlled. These updates are ready for manual deployment. The user reported the existing site at `http://sincioco.com/sinstar/novel/`; browser offline storage there requires HTTPS. This local update does not change hosting or publish files.

Browser behavior references: [audible playback permissions](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play), [service workers and HTTPS](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers), [media Range request forwarding](https://web.dev/articles/sw-range-requests), [storage estimates](https://developer.mozilla.org/en-US/docs/Web/API/StorageManager/estimate).

## Search and sharing metadata

The canonical reader URL is `https://sinstar.sincioco.com/BookOne/`. `production/seo_metadata.py` owns its title, description, author, canonical URL, social preview and truthful Book JSON-LD; `production/build_site.py` includes that metadata on rebuild. The existing CSP remains unchanged. All chapters remain in the initial HTML and the existing reader controls reveal them. Chapter fragments are navigation within this one page, not separate sitemap pages. Book markup does not promise a Google rich result. Runtime following, story, cues, audio and saved-position identity are unchanged by these metadata edits.

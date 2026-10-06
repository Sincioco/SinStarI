# Sin Star — Book One: web reader

Deployment-ready static website, built from the original novel HTML. **42 chapters plus the new title introduction**, with the accepted Michael/Bella/Uncle_Fu/Aiden performance. Audio is the approved mono 32 kbps mobile edition; the title introduction uses Michael at speed 0.97 and says exactly **“Sin Star. Book One. Created by Sin.”** Audio totals **72,303,282 bytes** (72.3 MB). No synthesis happens in the browser.

## Preview and deployment

For local preview, serve this folder with an existing Python installation:

```sh
python -m http.server 8894 --bind 127.0.0.1
```

Open `http://127.0.0.1:8894/`. The current desktop preview is served from the parent directory at `http://127.0.0.1:8894/web/`. Opening `index.html` as a file URL does not support module loading/offline storage. No .NET build is required.

Copy these files together to any HTTPS directory on sincioco.com, preserving relative paths: `index.html`, `reader.css`, `app.js`, `offline.js`, `sw.js`, `book.json`, `manifest.webmanifest`, `icon.svg`, `storyboards.json`, and the complete `audio/` directory. Include any later registered storyboard image files too. `production/` and this README are authoring/test records and can stay local. Deployment and hosting account access are separate from the authorized repository commit and push.

The server must serve JavaScript modules with a JavaScript MIME type, MP3 as `audio/mpeg`, and JSON as JSON. Keep `sw.js`, HTML and JavaScript revalidating rather than permanently cached. Standard HTTP Range support is useful for streamed audio. All references and the service-worker scope are relative to this folder; no domain, root-path rewrite, external font, CDN, analytics or paid service is required.

## Reading and listening

First visit opens the title page and attempts playback. Browsers commonly block audible autoplay: **Play** starts it when required. Returning visits restore the chapter and timestamp for the same audio/content revision, then attempt playback again. Browser/private-mode storage restrictions are handled without blocking online reading.

Select a chapter to play it. Previous/Next, Play/Pause, seek, font-size controls and keyboard-accessible buttons are provided. Chapter endings advance automatically; the epilogue ends without looping. The controls prevent overlapping audio and discard stale loads after rapid navigation.

Yellow highlighting follows **actual production chunk boundaries** (phrases or paragraphs), not invented word timings. All 3,048 cues were matched against the original text. Small MP3 decoder/encoder timing differences are possible; a long phrase is highlighted as a whole. Pause, seek, cue gaps, errors, changed text and missing cue elements clear old highlights. Headings and title-page text have no invented alignment. Follow narration scrolls an offscreen active passage into view; manual wheel/touch reading disables following until you check it again. Reduced-motion preference is respected.

## Offline audio

Open **Offline audio** and choose **Download this chapter** or **Download whole book**. There is no automatic whole-book download. Downloads run sequentially, show progress and support cancellation/retry; completed chapters are kept. Full byte count and SHA-256 are verified before a chapter is marked saved. HTTP 206/truncated files, insufficient quota, cancellation and write failures cannot produce a false completed badge.

Saved browser copies are selected first and played as one bounded chapter Blob at a time. The service worker also handles byte ranges correctly (206/416) for cached audio. Missing chapters fall back to the network; when unavailable, the reader explains that the chapter must be downloaded or the connection restored. Network audio uses `no-store` so hidden HTTP cache copies do not defeat explicit removal. The page, complete text, controls and cue data are cached for reload offline.

Use **Remove this chapter** or **Remove all offline audio** to reclaim space. Audio revision hashes prevent stale editions from being used. Browsers can evict cache storage; private browsing may restrict it. Check the saved badges before leaving connectivity. This browser storage is separate from Files/Downloads. **Save this MP3 to Files** is a separate ordinary download; the website cannot automatically inspect arbitrary phone files. Keep the page open while downloading; background or closed-tab downloads are not promised.

## Add storyboard pictures later

See [STORYBOARDS.md](production/STORYBOARDS.md). Stable chapter/block/cue attributes make alignment independent of DOM positions. Insert figures between existing passages; preserve the prose spans and their IDs. Captions and pictures are excluded from narration. No storyboard images were fetched or invented for this website.

After presentation or image changes, run `python production/refresh_cache.py` to update the offline shell version without changing audio or prose. It includes images explicitly listed in `storyboards.json`. **Do not rerun `production/build_site.py` after hand-editing the web content** unless you intend to regenerate `index.html` from the original source HTML and overwrite those web-only edits. The original source remains untouched.

## Verification and limits

Chrome desktop and responsive phone viewport checks are recorded in `production/browser-validation.json`. Original rendered prose was compared exactly for all 42 chapters, all 43 MP3 hashes/durations/codecs checked, and title audio fully decoded. Tests cover stable cue matching, inserted image/caption, edited-text failure, pause, resume, navigation races, storage failure, download cancellation/retry, quota, rejected partial response, whole-book download, range seeking, deletion and the final chapter ending. Offline reload/seek/auto-next/missing-chapter checks run with the local HTTP server stopped. `production/browser_checks.html` is the optional local verification fixture; it uses this origin's playback/cache state and is not needed for deployment.

No physical phone/Safari test or subjective listening claim is made. Autoplay and browser storage remain browser-controlled. Files are ready for your deployment; the website has not been deployed to sincioco.com.

Browser behavior references: [audible playback permissions](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play), [service workers and HTTPS](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers), [storage estimates](https://developer.mozilla.org/en-US/docs/Web/API/StorageManager/estimate).

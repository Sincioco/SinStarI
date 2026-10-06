# Adding illustrations without shifting narration

`index.html` owns presentation. `book.json` owns chapter/audio identities and timed narration cues. Audio files retain their SHA-256 identities. A cue looks up exact `data-cue-id` values and checks normalized words plus their hash, independently of element positions or paragraph numbers.

Existing paragraphs have stable IDs such as `ch-00-b0002`; narrated spans have IDs such as `data-cue-id="ch-00-s0001"`. A phrase crossing emphasis/paragraph boundaries can have several spans carrying the same cue ID. Preserve all of them and their original words. Do not renumber IDs when inserting content. Do not add a cue ID to a caption.

Insert a figure **between** existing paragraphs, for example before the paragraph whose ID is `ch-00-b0002`:

```html
<figure id="scene-c00-s01" data-no-narration="true">
  <img src="images/c00-s01.webp" width="1280" height="720"
       alt="Describe the actual illustration for readers who cannot see it."
       loading="lazy" decoding="async">
  <figcaption>Your optional caption.</figcaption>
</figure>
```

This is an authoring example; no image with that filename is supplied. Keep real image paths relative and inside the web folder. Width/height reserve layout space; ResizeObserver also rechecks the active passage after layout changes. Figure/caption text is excluded even if accidentally placed near a spoken span. If a narrated phrase is edited or a target is missing, the reader clears the highlight instead of guessing a different passage.

Register each real image for offline reading in `storyboards.json`, for example `{"images":["images/c00-s01.webp"]}`, then run `python production/refresh_cache.py`. This refreshes the shell cache only and preserves existing audio downloads. Images in this explicit registry are cached with the page; consider their size before adding many. The audio download total shown to readers refers to audio only.

Do not rerun the full HTML builder after hand-authoring illustrations unless you intend to recreate the website from the original HTML. Keep a source-control checkpoint of your web edits. No source novel/manuscript changes are required for illustration insertion.

A Chrome test inserted a temporary image and caption before an active paragraph, confirmed the same stable phrase remained highlighted, then edited that phrase and confirmed the previous highlight cleared. The temporary fixture was removed; no test illustration remains in the production book.

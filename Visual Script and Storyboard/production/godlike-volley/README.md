# C00-S01 — Moving Godlike (September 27, 2026)

Sin requested fast physical action from Kael, rapid earth/fire/lightning volleys,
Arin dodging and being knocked off his feet, the recognizable violet sword,
and an ending matching the first frame of **Who Are You**. The former Godlike
clip remains unchanged. This is an additional take, not a replacement selection.

## Delivery and generation

- Local final: `../../asset/videos/hover/C00-S01_Clip4 - Wide - Moving Godlike.mp4`.
- 12 seconds, 288 frames, H.264/AAC, **1280 × 720**, 24 fps, landscape 16:9.
- Raw source: `../render-sources/godlike-moving-volley-take1.mp4` (local, never Git).
- `dynamic-start.png` was generated with the built-in image tool from the existing
  Godlike keyframe, `../references/c00-s01-duel/Kael Weapon - Front View.png`, and
  Arin's approved 4K head contact sheet. The brief puts Arin in an evasive sidestep
  and Kael in an advancing lunge, preserving the shield, cyan sword, black silhouette
  and violet starfield blade with its star/crescent guard. It is a scene frame;
  the labeled head-reference grid is not animated.
- `volley.json` records the complete motion/negative prompts, seed and size.
  `queue_volley.py` reuses the established two-pass LTX 2.5 graph and final-size
  owner. Both sampling passes condition on the exact next-shot opening frame.
- LTX samples **1280 × 768** and center-crops to 720p. Conditioning images are
  fitted to 1280 × 720 and padded 24 pixels above/below before sampling. The output
  is not an upscale of a lower-resolution generated video.
- `volley-api.json`, `volley-ui.json`, receipt and execution history retain the
  reproducible job. The editable UI workflow is also in ComfyUI's saved
  **Sin Star I Prologue Episode / C00-S01 - Moving Godlike Volley - 720p** folder.

## Finishing and validation

The render shows advancing footwork, a lunge/turn, stone strikes, fire, lightning,
Arin's knockdown and recovery, then Kael shrinking into the distance. The dark
silhouette and violet blade remain recognizable; bright spell effects briefly
occlude parts of both fighters. As with other generated action, fine weapon and
face details vary during fast motion; this is not a frame-by-frame identity guarantee.

The next shot is `C00-S01_Clip2 - Wide - Who Are You.mp4`. Its decoded first frame
is preserved in `references/next-first-frame.png`. The final 0.5 seconds blends
over ten frames into that actual frame, scaled to 720p; the last two frames hold
the exact source composition and poses. Final decoded-frame SSIM against that
scaled reference is **0.982656** (compression prevents pixel identity).

FFmpeg fully decoded the final video/audio without errors; dimensions, frame count,
duration and audio level passed. Sampled action frames were inspected at three
frames per second and the finished video was played in Chrome. The final frame
is also preserved for continuity inspection. Original media bytes are unchanged.

Script, Storyboard and Video Clips all register stable ID
`new-c00-s01-duel-moving-godlike`. Existing remembered selections are preserved.
The new take is included by default in the next review render; the user can mark
**Exclude From Movie**. No YouTube upload or full movie regeneration was requested.

Use Ctrl+F5 for updated browser assets. No .NET rebuild is required.

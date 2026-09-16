# C00-S01 — The Concealed Opponent

The delivered edit is **14 seconds**, 336 frames at 24 fps, landscape 16:9.
It plays as clip 3, followed by its new **Godlike** variation and **Wide / Unreachable**, and appears before
that illustration in both Script and Storyboard. The existing wide clip is unchanged.

## Story and continuity

- Arin attacks, is knocked down, rises and is driven onto his knees again.
- The opponent remains unhurt and composed. Arin recovers into a defensive guard.
- A brief teleport leaves the opponent standing far away on the right, with Arin
  in the left foreground for the cut into the existing wide shot.
- The opponent's face and body surfaces remain blacked out. Its established
  body outline is retained; no hood or new costume was added.
- The violet starfield blade and circular star guard remain recognizable. This
  weapon is Arin's later recognition clue. The review notes describe this payoff;
  the unchanged script still treats the dream as unconfirmed contact or prophecy.

## Files and reproduction

- Final local preview: `../asset/videos/hover/C00-S01 - Close - Effortless.mp4`.
- Final keyframe: `../asset/images/c00-s01-duel.png`.
- [Shot specification, prompts and frame-accurate edit list](c00-s01-duel.json).
- `references/c00-s01-duel` preserves the supplied Kael body/weapon views and
  Arin model references, plus the superseded starting concepts.
- `workflows/new-c00-s01-duel-concealed*.json` contains the LTX 2.5 API/UI graphs.
  Matching ComfyUI receipts are in `renders/history` and `queue-receipts.json`.
- `renders/clips` retains all generated takes locally. The final edit uses the
  reviewed sections specified by `edit_segments`, then exports its 1024 × 576
  source at 960 × 540 with original generated audio. Each audio cut has a 25 ms
  fade to avoid clicks. No music or dialogue was added in editing.
- Keyframes were generated and revised with the built-in image-generation tool.
  Video uses the installed LTX 2.5 distilled 22B model and FFmpeg for editing.

The full takes are production material, not additional playlist entries. One take
made the opponent recoil; that section is excluded. Another had shield placement
drift, so its use is restricted to the teleport beat; the final held pose uses
the corrected shield framing. The edit uses deliberate camera cuts between beats.

## Validation

Reviewed sampled frames across all takes and the final edit for hidden identity,
visible sword, repeated Arin knockdowns, teleport and final composition. The final
file fully decodes with H.264 video and non-silent AAC audio at 24 fps and 16:9.
The new review text fits both overlay and side-by-side rendered panels. The site
validator preserves existing artwork/video checksums and script/canon prose;
player interaction checks pass with 136 clips. Chrome loaded the updated sequence
and listed the new duel as clip 3 before the existing wide shot.

The current JSON includes this clip in the next full review render. The previous
full review MP4 and its upload checkpoint remain separate from this clip delivery.
The new preview is pending YouTube upload; no upload was attempted during this task.

No .NET rebuild or server restart is required. Use Ctrl+F5 in the browser.

## Clip 2 — Godlike (September 16)

Sin approved the new giant-Kael starting image in
`references/c00-s01-duel/godlike-keyframe.png`. It was generated with the built-in
image tool using the accepted duel artwork and supplied front sword reference.
The original illustration and Clip 1 remain unchanged.

The new **12-second**, 288-frame, 24 fps variation shows a towering concealed
opponent hurling boulders, striking Arin with lightning and blasting him off his
feet with fire. The shadow remains composed, then shrinks and recedes into the
distance while Arin recovers. Its violet sword remains the recognition clue.
This is visual foreshadowing of Aevos; the early dream's cause remains unexplained
in the script. C04-S03 still establishes Kael's later deliberate contact/training.

- Final local file: `../asset/videos/hover/C00-S01_Clip2 - Wide - Godlike.mp4`.
- [Image prompt, LTX prompts, receipts, checksum and edit list](c00-s01-godlike.json).
- First take supplies lightning, fire, the knockdown and shrinking retreat.
  A focused second take supplies rocks visibly traveling toward Arin; the first
  take's weaker falling-rock opening is excluded. The edit has one deliberate cut.
- Both shots were appended to ComfyUI's existing queue and completed successfully.
  Their API/UI workflows and history receipts are preserved; MP4 sources stay local.
- Script and Storyboard expose Clip 1 / Clip 2 with the existing shared Remember
  preference. Neither the default nor an existing remembered selection was changed.
- Live Sequence Review lists **Clip 2 / Godlike as clip 4**, followed by Unreachable
  as clip 5. Its JSON entry is also included in the next full review render.
- Reviewed sampled frames of both takes and the final edit. The final H.264/AAC
  preview is exactly 960 × 540 (16:9), fully decodes, and retains generated audio.
  Site, preview interaction and live-player checks pass with 137 clips.

The new clip is pending YouTube upload alongside the existing backlog. The full
review movie has not been rendered again as part of this clip request.

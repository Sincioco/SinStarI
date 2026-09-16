# C00-S01 — The Concealed Opponent

The delivered edit is **14 seconds**, 336 frames at 24 fps, landscape 16:9.
It plays as clip 3, immediately before **Wide / Unreachable**, and appears before
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

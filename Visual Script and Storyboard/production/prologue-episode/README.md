# Sin Star I — Prologue: Room for One

## Delivery

Completed locally on September 27, 2026. The episode covers C00-S01 through C00-S03 in **3 minutes 7 seconds**, with 24 narrative shots, the original 4K poster for exactly the first two seconds, and closing title/creator/project credits. The optional emergency-contact response is **Leave it blank.**

- YouTube: [Watch the full episode — Unlisted](https://youtu.be/1IGh0JRry4U)
- Local episode: `../../asset/videos/Sin-Star-I-Prologue-Room-for-One-Episode.mp4`
- Website: `../../movies.html#prologue-episode`
- Selected awakening: **C00-S01_Clip7 - Wide - Wake**. Arin wakes in visible horror with a sustained **Nooooooooooo!**, followed by the neighbor and his exact reply. Earlier versions remain selectable.
- No burned-in subtitles in delivered clips or the episode.
- Landscape 16:9, 24 fps throughout. New LTX 2.5 source clips are **1024×576**; the episode is a **3840×2160 upscale** with a native 4K poster. The export does not create native 4K character detail.

## Continuity and preserved takes

Existing family, Arin, Kael, armorer, clerk, dream-fight and Earth-intervention clips supplied the continuity references. The dream opponent remains concealed with his established violet sword. The father now says: “He’d say that if you tied him to the chair.”

There are **23 new LTX generation takes plus one corrected sound edit**, all available as 24 new alternatives in Script and Storyboard. No original or generated clip was deleted. Sources stay in `../render-sources/prologue-episode`; delivery copies stay in `../../asset/videos/hover`. Videos are intentionally excluded from Git.

Some LTX takes generated subtitles despite their prompts. Only the delivery derivatives are cropped and scaled to remove them; unedited sources remain local. The original distant-disturbance take speaks an invented word. Its episode edit replaces that word with the earlier wordless dream cue. Wake takes 1–3 are retained for comparison; take 1 speaks unwanted stage-direction words, and takes 2–3 did not achieve Sin’s requested sustained horror.

## Regenerating a clip

Open ComfyUI at http://127.0.0.1:8191, choose Workflows, and open **Sin Star I Prologue Episode**. The folder contains 23 workflows using the established clip filenames. The corrected wake workflow is **C00-S01_Clip7 - Wide - Wake**. Each stores its image, prompt, dimensions and seed. Input images are copied to the top level of ComfyUI’s input directory so its UI picker can find them; API-only subfolder references were corrected. Press Run to regenerate locally; no upload happens automatically.

Workflow library on this machine:
`D:\Sin - AI Prompt\work\comfy_photo_video_user\default\workflows\Sin Star I Prologue Episode`

Repository copies are under `shots/*-ui.json` and `shots/*-api.json`; the first family shot uses the `pilot`/memory files in this folder. Source keyframes are in `images` or the existing `../../asset/images`. API queue receipts preserve the actual submitted prompt. ComfyUI also embeds workflow metadata in raw generated MP4 files. A regenerated raw clip may still need the same editorial crop specified in `accepted.json`.

## Small production tools

- `episode.json` owns shot order, action, dialogue, poster duration and credit wording.
- `queue_shot.py` creates the API/UI workflows and submits one shot; an existing receipt prevents accidental resubmission. Use a new take ID and filename for a new attempt.
- `monitor_clips.py` collects completed renders and writes raw audio/visual review evidence.
- `finish_clip.py` records a reviewed take and any explicit crop/sound edit in `accepted.json`. `episode_use` distinguishes final selections from preserved alternatives.
- `publish_clips.py` updates the existing media catalog and only the matching illustration controls in Script/Storyboard.
- `assemble_episode.py` creates the poster, selected narrative cuts and credits, then exports the episode. It uses the existing local FFmpeg/NVENC installation.
- `validate_workflows.py` checks all 23 reference images against ComfyUI’s current picker choices, matching API/UI copies and 16:9 dimensions.
- `validate_episode.py` transcribes dialogue from the assembled MP4 using the already-installed Faster Whisper runtime. It checks the sustained scream separately because full-shot ASR can omit a long vowel.

Run these from `Visual Script and Storyboard` with the installed Python runtimes. No dependencies were installed. The live-review settings in `../review-sequence` are not modified by this pipeline.

## Validation

- All **14 dialogue passages** in the final assembled MP4 matched their written words, allowing punctuation, elongated “No”, and the documented Neris/route ASR spelling variants. Evidence: `episode-validation.json`.
- Opening poster boundary inspected at frames 47 and 48: poster then black, exactly two seconds at 24 fps.
- FFmpeg decoded the entire final episode successfully; dimensions, frame rate and audio stream verified.
- Static website validation passed: 4 HTML pages, 1,382 local references, 161 clips, unchanged canonical narrative and 130 unchanged original renamed-video hashes.
- Chrome browser check: Clip 7 selected in both views, new wake video decoded at 1024×576 and played, shared Script navigation worked.
- ComfyUI workflow library visibly lists all 23 generation workflows. Corrected wake workflow passed UI queue validation, including LoadImage and conditioning. The validation-only rerun was canceled before video output; it was not an additional completed render. Workflow left open.
- Speech-to-text verifies wording; it does not prove acting quality or perfect lip sync. Sin can review performance through the links below.

## Uploaded clip alternatives

All links below were verified Unlisted in YouTube Studio through the signed-in Codex in-app browser.

| Clip | Episode selection | YouTube |
| --- | --- | --- |
| C00-S01_Clip2 - Close - Memory | Selected | [Watch](https://youtu.be/apZVZPnJ58s) |
| C00-S01_Clip3 - Wide - Receding Door | Selected | [Watch](https://youtu.be/fIgIhzJIZiU) |
| C00-S01_Clip2 - Wide - Who Are You | Selected | [Watch](https://youtu.be/-4SfKxmfZ48) |
| C00-S01_Clip2 - Wide - One Pillow | Selected | [Watch](https://youtu.be/KbBtYPvVGpE) |
| C00-S02_Clip2 - Medium - Neris Issue | Selected | [Watch](https://youtu.be/ikK8z_xYzWA) |
| C00-S02_Clip3 - Medium - Proper Work | Selected | [Watch](https://youtu.be/14ridijmafM) |
| C00-S02_Clip2 - Close - Contract | Selected | [Watch](https://youtu.be/vlS_B6-6fZI) |
| C00-S02_Clip3 - Close - Recovery Fee | Selected | [Watch](https://youtu.be/xLPZGcyQoOA) |
| C00-S02_Clip4 - Close - And The Crew | Selected | [Watch](https://youtu.be/qyUfT67iRQw) |
| C00-S02_Clip5 - Close - Group Contracts | Selected | [Watch](https://youtu.be/AkPNDZB7B5k) |
| C00-S02_Clip6 - Close - Join A Group | Selected | [Watch](https://youtu.be/GjHQFtelcW4) |
| C00-S02_Clip7 - Close - Leave It Blank | Selected | [Watch](https://youtu.be/FPkmzGCg9g4) |
| C00-S01_Clip3 - Close - White Fire | Selected | [Watch](https://youtu.be/92PO6KZIltM) |
| C00-S01_Clip3 - Wide - Unspoken Sound | Selected | [Watch](https://youtu.be/m6WMUXnL5wI) |
| C00-S01_Clip3 - Wide - Ledger Strap | Selected | [Watch](https://youtu.be/cRN89dqJMi0) |
| C00-S01_Clip4 - Wide - Wake | Retained alternate | [Watch](https://youtu.be/2w86auyzt5U) |
| C00-S01_Clip5 - Wide - Wake | Retained alternate | [Watch](https://youtu.be/ro6UL9cIQL0) |
| C00-S02_Clip4 - Wide - Ration Shared | Selected | [Watch](https://youtu.be/xmHoUEcoc4c) |
| C00-S02_Clip5 - Wide - Wrong District | Selected | [Watch](https://youtu.be/Yic7LzssEVs) |
| C00-S03_Clip2 - Wide - Distant Disturbance | Retained alternate | [Watch](https://youtu.be/vroqA2D40wk) |
| C00-S03_Clip3 - Wide - Distant Disturbance | Selected | [Watch](https://youtu.be/gXBi20ULxJk) |
| C00-S03_Clip4 - Wide - Not Mine | Selected | [Watch](https://youtu.be/_jRXqX-2UUU) |
| C00-S01_Clip6 - Wide - Wake | Retained alternate | [Watch](https://youtu.be/KpuRW9dw6ac) |
| C00-S01_Clip7 - Wide - Wake | Selected | [Watch](https://youtu.be/cMbq0MbVwXc) |

Created by: **Louiery R. Sincioco (Sin)**. Sin Star is the first game project to use the new SMILE Programming Language, Compiler, Libraries and Tool Chain. Open-source project: https://github.com/sincioco/smile-2.0

## Implementation scope

The episode manifest owns narrative order; small queue, collection, editorial, publication, assembly and validation tools own their respective operations. Existing website rendering/catalog owners receive only focused additions. No frontend dependencies or framework were added. New utility files remain below 120 lines each; most added JSON is reproducible ComfyUI graph data. No architecture exceptions were required.

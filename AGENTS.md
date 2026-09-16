# SinStarI Working Instructions

- This repository is the home of Sin Star I. The game project may move here later; do not move it without a request.
- Work directly in `Visual Script and Storyboard` for all Script and Storyboard edits. This is the canonical local working copy.
- Preserve the existing artwork, narrative, shared navigation, theme, audio and remembered clip selections unless a request changes them.
- Keep artwork, templates, prompts and render sources needed for authoring inside this folder. External tools such as ComfyUI remain installed separately.
- Generate future videos in landscape 16:9 unless Sin explicitly requests another format. Set the generation dimensions to 16:9 and verify the exported video's aspect ratio before delivery.
- Do not generate ZIP deliveries unless Sin explicitly requests one.
- Never stage or commit video files, including MP4 files. Check the Git index before every commit. Keep local copies in `asset/videos` and render sources in `production/render-sources`.
- Name hover videos `C00-S01 - Close - Memory.mp4`; append variations after the scene ID, for example `C00-S01_Clip2 - Close - Memory.mp4`. Keep stable media IDs for saved choices.
- Record verified YouTube uploads in `production/youtube-uploads.json`. Use Unlisted visibility unless Sin requests otherwise. Never record an upload as complete before YouTube confirms it.
- Use the signed-in Codex in-app browser for YouTube uploads; external Chrome is a fallback only if that fails. Never store session credentials.
- Missing previews must fail quietly, log diagnostic information to the console and retain the illustration. Use the matching verified YouTube clip when available.
- Use exactly one Codex agent for this project. Keep implementation simple and reuse installed tools; do not install dependencies.
- Write detailed commit messages. Prefix every Codex-created commit subject exactly with `Sin and Codex: `.
- For static changes, no .NET compilation or app restart is needed. Refresh the browser with Ctrl+F5 and version changed assets.

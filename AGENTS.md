# SinStarI Working Instructions

- This repository is the canonical home of the native Sin Star I game at the root and its visual story production under `Visual Script and Storyboard`. The compiler, shared libraries and Studio remain in the sibling `D:\SMILE 2.0` repository.
- Studio is the authoritative version of Battle Systems, Battle Simulations, and Towns/Maps. Sin builds and approves these in Studio, then their implementation and authored content are brought into Sin Star I. Preserve Studio behavior when integrating or copying them here; do not create a separate or divergent game implementation. Reuse the existing shared owners where practical. Game-specific title navigation and lifecycle may wrap the Studio version. Make changes to these shared systems in their Studio workflow first unless Sin explicitly requests otherwise.
- Work directly in `Visual Script and Storyboard` for all Script and Storyboard edits. This is the canonical local working copy.
- Preserve the existing artwork, narrative, shared navigation, theme, audio and remembered clip selections unless a request changes them.
- Keep artwork, templates, prompts and render sources needed for authoring inside this folder. External tools such as ComfyUI remain installed separately.
- Generate future videos at 720p (1280 x 720), landscape 16:9, unless Sin explicitly requests another resolution or format. Apply this target when preparing new generation workflows and verify exported dimensions before delivery. Do not silently substitute a lower-resolution generation and call its upscale native 720p.
- For future LTX 2.5 videos featuring Arin, use `Visual Script and Storyboard/production/character-references/arin-head-contact-sheet-2x2-4k.png` as the approved face/hairstyle identity reference. Use the appropriate head view when preparing scene keyframes, together with established body/costume and scene-continuity references. Do not animate the labeled grid as a scene. Compare generated faces with the sheet; reference conditioning improves consistency but is not an identity guarantee.
- Do not generate ZIP deliveries unless Sin explicitly requests one.
- Never stage or commit video files, including MP4 files. Check the Git index before every commit. Keep local copies in `asset/videos` and render sources in `production/render-sources`.
- Name hover videos `C00-S01 - Close - Memory.mp4`; append variations after the scene ID, for example `C00-S01_Clip2 - Close - Memory.mp4`. Keep stable media IDs for saved choices.
- Record verified YouTube uploads in `production/youtube-uploads.json`. Use Unlisted visibility unless Sin requests otherwise. Never record an upload as complete before YouTube confirms it.
- Use the signed-in Codex in-app browser for YouTube uploads; external Chrome is a fallback only if that fails. Never store session credentials.
- Missing previews must fail quietly, log diagnostic information to the console and retain the illustration. Use the matching verified YouTube clip when available.
- Use exactly one Codex agent for this project. Keep implementation simple and reuse installed tools; do not install dependencies.
- Write detailed commit messages. Prefix every Codex-created commit subject exactly with `Sin and Codex: `.
- For static story changes, no .NET compilation or app restart is needed. Refresh the browser with Ctrl+F5 and version changed assets. For game changes, run `Build.ps1` and relaunch `bin/Release/SinStarI.exe`.

## Architecture and controlled growth

- Before substantial game changes, read `docs/ARCHITECTURE.md`; for story changes, read `Visual Script and Storyboard/production/README.md`. Then inspect the implementation and its callers. Identify the behavior's owner, state, dependencies, expected growth and validation before editing.
- Reuse cohesive modules. Keep launchers and entry points focused on startup, wiring, delegation and shutdown; place UI, playback, persistence and rendering behavior with their respective owners.
- Pass only the state a module needs. Avoid dependency cycles, broad mutable globals, generic manager modules and replacement monoliths.
- Make only the smallest extraction needed for the requested change. Preserve public formats and existing behavior, capture behavior before risky extraction, and keep structural moves distinguishable from behavior changes. Record unrelated debt instead of starting a broad refactor.
- Review changed handwritten source for physical-line growth and responsibility drift. Respect established no-growth baselines; never silently raise budgets, broaden exclusions or compress code to bypass a check.
- Run relevant existing validation and available architecture checks. Report actual results, changed-file growth, ownership changes, exceptions and unvalidated behavior. Update ownership notes when boundaries change.
- Architecture review is currently manual: no automated size/dependency gate or reviewed numeric baseline is installed. The reusable kit at `D:\Sin - AI Prompt - Contents\2026-09-12-0851 Codex Architecture Guardrails` supplies proposed budgets and future checker guidance; tailor source/data classifications and test pass/fail behavior before adopting an enforced gate. Its alternative project prompts do not authorize additional product work.

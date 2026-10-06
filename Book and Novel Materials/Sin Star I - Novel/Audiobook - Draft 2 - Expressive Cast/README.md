# Sin Star I — Book One, Draft 2a

Accepted Draft 2 performance with Draft 2a chapter tags: **5:00:59.865**, prologue, 40 chapters, epilogue. Play the 42 numbered MP3s or the M3U playlist. Every chapter is 24 kHz mono / 96 kbps.

Final cast: **Michael narrates; Mira is Bella; Kael is Uncle_Fu; Arin is Aiden**. Other roles are in `cast-and-direction.json`. The exact authoritative manuscript remains one directory above; its SHA-256 is `c5a45cba2c5a3cb5fcfeffbc6f06ef99bcaa5364ce9988705451479c93ad9f72`. All 42 plans preserve its narrative word order and account for 3,048 chunks. They also preserve scene direction and speaker-attribution decisions. No prose was summarized or rewritten.

## Rebuild combined editions without speech synthesis

With Python 3, FFmpeg and ffprobe already installed, run from this folder:

```sh
python rebuild_editions.py --formats mp3 m4b
```

The command checks chapter SHA-256 values, then writes to ignored `rebuilt-editions/`. MP3 joins encoded frames without re-encoding. M4B encodes AAC from the chapter recordings and adds 42 chapter markers. `--formats mobile` creates a 32 kbps MP3. Existing outputs are not overwritten; choose another `--output` directory when necessary. These are rebuilds from the committed MP3s, so the M4B/mobile files are a further lossy generation and will not match the original FLAC-derived local masters byte-for-byte. Small duration differences can occur from codec delay at joins.

## Production and verification

`release-manifest.json` provides relative paths, exact chapter hashes, tags, durations and clip boundaries. `chapter-manifest.csv` is a compact source-heading/output map. `plans/` retains exact synthesis text and final voice assignments. `production/engine-settings.json` and `production/pronunciation.json` preserve model revisions, settings and pronunciation. New synthesis can vary from the accepted repaired takes; use the committed MP3s to preserve the approved performance.

`QA REPORT.md` and `qa-summary.json` record local production validation. Only 140 Mira clips were replaced; 2,908 other raw takes remained byte-identical. The source, all 42 chapter hashes and current tags are checked again for this commit. Chapter loudness ranged from -19.53 to -19.48 LUFS, maximum measured true peak -1.74 dBTP. Six ASR differences were reviewed; automated checks cannot establish perfect phonemes or acting. No subjective listening is claimed by the producer.

Chapter metadata: Artist **Produced by Sin**, Album **Sin Star I - Book One**, Title **Sin Star I - Book One - Draft 2a - {actual filename stem}**. See `AUDIOBOOK-METADATA.md` for the reusable updater. Change `draft_label` for future drafts, or clear it for the final edition.

`production/comfyui/` exports the separately requested **Sin - AI Voices - Text to Speech** workflow and node using configurable local runtime paths. The installed desktop copy was not changed during this repository export.

## Storage scope

Git contains all 42 accepted chapter MP3s. The original complete MP3 (216,723,399 bytes) and M4B (234,493,597 bytes) exceed GitHub's 100 MiB regular-file limit and stay local. Duplicate mobile chapters, the 72,243,879-byte mobile combined book, seven phone parts, raw chunks/FLAC/WAV, auditions, previous Serena revision, staging data, restore backups, machine paths, model weights/environments and Library delivery identifiers remain local and are not committed. No Git LFS or paid storage was introduced. Draft 1 is outside this change.

Models were already installed: Kokoro-82M and Qwen3-TTS CustomVoice, both Apache-2.0 model releases. Synthesis ran locally without a manuscript-upload service, paid API, credential-file access or real-person voice cloning. No game/compiler code, source manuscript, .NET build or browser refresh is involved in this delivery.

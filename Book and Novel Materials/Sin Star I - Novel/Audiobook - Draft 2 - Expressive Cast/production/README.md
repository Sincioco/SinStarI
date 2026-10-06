# Production archive

The committed chapter recordings are the accepted performance. `../plans` retains every original text chunk, final speaker/voice and direction; `../cast-and-direction.json` is the cast authority. Settings and pronunciation are stored here. Model weights are obtained separately under their original licenses; nothing here installs them.

Kokoro generated Michael narration and Bella dialogue at speed 0.97. It used the pronunciation lexicon for both voices. Qwen CustomVoice generated remaining dialogue using each plan's preset and contextual direction. Segment checkpoints were keyed by exact text hashes; local ASR reviewed 3,048 segments. Repair passes corrected flagged omissions/articulation before mastering. The final Bella pass replaced 140 segments in 25 chapters and preserved all 2,908 other raw clips. New synthesis, even with the same seeds/settings, may differ because of batching, runtime and reviewed repairs.

Mastering used bounded per-segment active RMS matching, 5 ms fades, 0.10/0.18-second pauses and two-pass chapter loudness normalization. Original local combined editions were built from the normalized FLACs. `../rebuild_editions.py` rebuilds from the committed accepted MP3 chapters without requiring GPU/TTS, and documents the resulting generation difference.

`metadata-validation.json` records the completed 84-file metadata-only edit (42 committed chapters and 42 local mobile copies). FFmpeg encoded-audio hashes before/after matched and all other ID3 frames were preserved. It intentionally contains no local restore paths or account data. `repository-validation.json` records focused checks for this export.

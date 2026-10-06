# Sin - AI Voices - Text to Speech

Portable export of the separately installed ComfyUI tool, version 1.0.0. The installed desktop node is unchanged. This is a single-narrator tool; it does not reproduce the book's ensemble cast or apply the novel pronunciation dictionary.

Copy `sin_ai_voices_tts` into your existing ComfyUI `custom_nodes` folder. Before launching ComfyUI, set `SIN_TTS_PYTHON` to an existing Python interpreter with Kokoro 0.9.4, Misaki 0.9.4, PyTorch CUDA, NumPy and SoundFile. Configure `HF_HOME` to an existing Kokoro cache, and, when required on Windows, `PHONEMIZER_ESPEAK_LIBRARY`, `ESPEAK_DATA_PATH` and the eSpeak NG directory on PATH. FFmpeg must be on PATH. No package installer or model downloader is included; inference remains offline.

Import the workflow JSON. Select Text or File (local UTF-8 prose), choose a voice, and Run. Michael at speed 0.97 is the default. Existing voices: Michael, Fenrir, George, Lewis and Heart. This generic workflow's original voice selection is intentionally independent of the novel's final Mira/Bella cast.

Outputs appear beneath ComfyUI's output directory in `Sin-AI-Voices-TTS`. Chunk checkpoints support cancellation and resume with identical input/settings. Cancel stops only that job's subprocess. It saves 24 kHz mono WAV and 96 kbps MP3 and streams assembly from disk. Keep checkpoint files until completion.

The installed original passed typed/file input, alternate voice, empty/missing-input rejection, browser playback and cancellation/resume checks. A 100-chunk reading reused five completed chunks and finished 18:19.44; a separate 120,000-word check tested planning coverage only. This portable export changes only interpreter/cache/runtime configuration; compilation and focused configuration/chunk checks are performed for repository export, without rerunning GPU synthesis. No claim of subjective listening is made.

Model: https://huggingface.co/hexgrad/Kokoro-82M (Apache-2.0), cached revision `f3ff3571791e39611d31c381e3a41a3af07b4987`. Model weights, environments, private paths and account delivery records are excluded.

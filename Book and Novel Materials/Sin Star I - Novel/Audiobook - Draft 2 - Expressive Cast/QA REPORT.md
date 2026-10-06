# Sin Star I - Draft 2 - Mira Bella revision

Completed **5:00:59.86**, with the prologue, 40 chapters and epilogue in manuscript order. Source SHA-256 remains `c5a45cba2c5a3cb5fcfeffbc6f06ef99bcaa5364ce9988705451479c93ad9f72`.

## Final voices and scope

- Narrator: Kokoro **am_michael**, speed 0.97, unchanged.
- Mira: user-selected Kokoro **af_bella**, speed 0.97, replacing Serena.
- Kael: user-settled **Uncle_Fu**, unchanged. Arin: approved **Aiden**, unchanged.
- All other characters retain their existing presets and takes.

Only **140 Mira dialogue clips across 25 chapters** were regenerated. The other **2,908 raw audio clips are byte-identical**, verified by SHA-256. The 17 chapters with no Mira dialogue reuse their previous audio files. Chapter mastering was rebuilt where Mira appears; this may adjust overall chapter level while preserving other takes.

Mira uses Kokoro's natural prosody and the established name-pronunciation dictionary. The earlier Qwen emotional instructions do not control Bella. Remaining Qwen characters retain contextual speaker attribution and emotional direction. Implicit speakers are editorial interpretations from dialogue tags, nearby actions and turn-taking; supporting characters may share presets. No real-person reference recording or voice cloning was used.

## Verification

- Rechecked all source chapter body words against the 42 plans; exact wording and order preserved. All 3,048 input chunks accounted for.
- All 140 new Mira clips passed local ASR/technical review. One line's articulation of 'planned' was clarified with a short word-boundary separation, then transcribed exactly. Two reduced-speech/orthographic ASR differences ('want to'/'wanna', 'stores'/"store's") are documented; source words were unchanged.
- Prior validated takes were reused. Every rebuilt chapter MP3, affected mobile chapter, combined MP3/M4B/mobile book and seven revision parts passed full decoding and duration checks. M4B has 42 chapter markers; chapter order is retained.
- Chapter loudness measures **-19.53 to -19.48 LUFS**; maximum measured chapter true peak **-1.74 dBTP**.
- No subjective listening is claimed. ASR cannot prove every phoneme, acting choice, accent or smooth-sounding boundary; those remain for listening review.

## Files and prior version

The full mobile MP3 remains at `mobile/Sin Star I - Draft 2 - Complete Audiobook - Mobile.mp3`, **72,243,879 bytes**. Full MP3 and chaptered M4B retain their established names. New mobile parts explicitly include **Bella Revision** in their names; use those for current playback. `chapter-manifest.csv`, `manifest.json` and `mobile-parts.json` map every output to the source.

The previous Serena version is preserved in `Superseded - Mira Serena - 2026-10-06`, including full formats, all chapter/mobile files, prior metadata and replaced checkpoints. Original Serena auditions and optional voice comparisons remain historical materials. The selected Mira audition is now `Character Auditions/Mira/Mira - Bella - Dialogue Audition`.

All synthesis was local using existing Apache-2.0 model releases. No model download, paid API or credential-file access was required. The authoritative manuscript, Draft 1 and SMILE runtime/source are untouched. See `cast-and-direction.json` for exact voice mapping and model references.

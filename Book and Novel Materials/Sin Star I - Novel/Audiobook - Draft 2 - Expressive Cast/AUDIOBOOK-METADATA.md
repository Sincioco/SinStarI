# Sin Star I audiobook metadata defaults

These are Sin's requested defaults for future **Sin Star I - Book One** chapter MP3s, including mobile chapter copies. They do not change the general ComfyUI text-to-speech workflow.

- **Title:** `Sin Star I - Book One - {Draft Label} - {Actual File Stem}`. Preserve the chapter number, complete chapter information and Unicode punctuation from the real filename; exclude only `.mp3`.
- **Artist:** `Produced by Sin`
- **Album:** `Sin Star I - Book One`

Current draft label: **Draft 2a**. Edit `draft_label` in `chapter-metadata-defaults.json` when the draft number changes. For a finalized edition, set it to `null` or `""`; the script then omits both the draft label and its extra separator. Do not leave Draft 2a hardcoded for future editions.

Current example:

`Sin Star I - Book One - Draft 2a - 00 - Prologue — The World He Ended`

Finalized example:

`Sin Star I - Book One - 00 - Prologue — The World He Ended`

## Apply after chapter generation

Use Python 3 with FFmpeg and ffprobe on PATH:

```powershell
python ./apply_chapter_metadata.py --apply
```

Run this command from the audiobook folder, or supply the script's full path. It reads the neighboring config and the local `manifest.json`, falling back to the portable `release-manifest.json`, and edits only the individual chapter MP3s listed there plus existing matching copies in `mobile`. Combined books, mobile parts, auditions, backups, superseded versions and Draft 1 are excluded. Filenames remain unchanged.

The script changes only ID3 title (`TIT2`), artist (`TPE1`) and album (`TALB`). Current files use [ID3v2.4](https://id3.org/id3v2.4.0-structure) with UTF-8 text. Untouched frames and encoded audio bytes are retained. FFmpeg packet hashes independently verify unchanged audio essence, while ffprobe verifies every requested Unicode tag value. No audio re-encoding or dependency installation occurs. Unsupported tag features stop staging safely rather than silently discarding metadata.

Every run saves original files, staged replacements and a restore/verification report beneath the sibling `Audiobook Metadata Backups` folder, outside the active audiobook chapter folders. `metadata-before` also retains the original integrity manifests. To restore a run, copy its `originals` files and `metadata-before` files back to the corresponding relative paths under the audiobook folder, after ensuring those files are not open or newer revisions have not superseded them.

Without `--apply`, the script only prepares and verifies staged copies. Locked files are kept staged and reported; it never closes or kills an application. After the user releases a lock, continue the same run with `--apply --resume 'FULL RUN FOLDER'`. The config must remain the same for a resumed run. The latest local report is `chapter-metadata-report.json`.

Reapply these project defaults after future chapter generation and refresh the chapter integrity manifests before delivery. Do not alter combined book/part metadata unless Sin requests that separately.

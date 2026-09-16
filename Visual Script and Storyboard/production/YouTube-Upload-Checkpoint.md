# YouTube Upload Checkpoint — September 17, 2026

## Current status

- 141 website videos in the catalog: 137 picture previews and four complete films.
- All 141 catalog entries now have verified YouTube links: 137 Unlisted picture
  previews and four existing Public films whose visibility was preserved.
- This session uploaded and verified the remaining 36 previews through the
  signed-in Codex in-app browser. Titles, scene captions and creator/SMILE/open-source
  credits were applied before saving each preview as Unlisted.
- All seven planet-throw variations have verified links.
- Both C00-S01 concealed-opponent duel clips now have verified links:
  [Effortless](https://youtu.be/ymJ5AavCPk8) and
  [Godlike / Clip 2](https://youtu.be/DWaVpMgKbaw).
- No uploads remain pending. All local video copies remain outside Git.

## Existing full review

[Story Video Sequence Review](https://youtu.be/OkQiFzdy1kk) was already Public
when this session began. YouTube Studio showed the source filename
`Sin-Star-I-Story-Video-Sequence-Review.mp4` and duration 11:48. Those match the
current local render (707.667 seconds, 137 clips). Its existing visibility and
metadata were preserved; no duplicate full movie was uploaded.

`review-sequence/validate_review.py` passed against the current local JSON and MP4:
1920×1080, 24 fps, 16,984 video frames, 139 chapters and AAC stereo at 48 kHz.
The render receipt and movie checksum match. The local source checksum is recorded
in the catalog; YouTube's transcoded bytes were not compared with the local file.

## Future uploads

1. Use the signed-in Codex in-app browser. Preserve verified uploads and stable IDs.
2. Run `python production/youtube_catalog.py --stage 15` from the website folder.
   The ignored `production/local-state/current-upload-batch.json` identifies the
   next pending files. Staging uses hard links; verify their checksums against the
   current catalog before selecting them in YouTube Studio.
3. Upload that batch through YouTube Studio. Apply the catalog titles and credits,
   select Unlisted, and verify YouTube's save confirmation for each video.
4. Record each confirmed result with
   `python production/youtube_catalog.py --record CLIP_ID YOUTUBE_ID`.
   The command refreshes the website's verified-link map and its cache version.
5. Validate the catalog and commit/push the records. Never commit video files or
   mark a file uploaded from transfer progress alone. If live review settings have
   changed, render and validate the full movie again before uploading a revision.

The durable inventory is `youtube-uploads.json`; the generated playback map is
`../asset/youtube-uploads.js`. YouTube may continue processing or checking an
upload after saving it. Save verification is not a claim that all platform checks
have finished.

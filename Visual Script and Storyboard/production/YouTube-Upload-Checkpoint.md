# YouTube Upload Checkpoint — September 16, 2026

## Current status

- 139 website videos in the catalog: 135 picture previews and four complete films.
- 104 verified YouTube links: 100 new Unlisted uploads, the earlier Unlisted
  planet-throw take, and three existing films whose current Public visibility was preserved.
- All seven planet-throw variations have verified links.
- 35 videos remain pending. Their local copies are complete and playable.

YouTube Studio displayed **Daily upload limit reached** for the last five files
in the attempted batch. Further uploads were stopped. No reset time was shown,
and changing browsers would not resolve an account upload limit.

The five rejected files were `new-c05-s04`, `new-c05-s05`, `new-c06-s01`,
`new-c06-s02` and `new-c06-s03`. They remain `pending`, along with the 29 previews
not yet attempted and the newly rendered Story Video Sequence Review. No unverified video ID was added to the website.

## Resume

1. Use the signed-in Codex in-app browser after YouTube permits more uploads.
2. Run `python production/youtube_catalog.py --stage 15` from the website folder.
   The ignored `production/local-state/current-upload-batch.json` identifies the
   next files. Staging uses hard links and does not copy the MP4 data.
3. Upload that batch through YouTube Studio. Apply the catalog titles and credits,
   select Unlisted, and verify YouTube's save confirmation for each video.
4. Record each confirmed result with
   `python production/youtube_catalog.py --record CLIP_ID YOUTUBE_ID`.
   The command refreshes the website's verified-link map and its cache version.
5. Repeat for the remaining pending entries, validate the catalog and commit/push
   the records. Never commit video files or mark a file uploaded from transfer
   progress alone. Do not duplicate the 104 completed uploads.

The durable inventory is `youtube-uploads.json`; the generated playback map is
`../asset/youtube-uploads.js`. YouTube may continue processing or checking an
upload after saving it. Save verification is not a claim that all platform checks
have finished.

# Local Organization — September 16, 2026

## Completed local checks

- 130 original hover clips renamed with SHA-256 equality; original bytes preserved.
- 135 unique hover clips for 129 pictures, including five new ten-second World Hurled takes.
- All five new files fully decoded with FFmpeg: H.264 video, AAC audio, 960×640,
  24 fps, audible soundtrack. Existing 130 media hashes retain their earlier decode evidence.
- Sampled every new take at 0, 2, 4, 6, 8 and 9.5 seconds. All show planetary impact,
  fragmentation, barrier failure and surviving heroes. Clip 3 was selected for the
  clearest overall sequence. These are generated concept variations; their choreography
  and camera movement differ. They are not gameplay recordings.
- 30 focused playback checks pass: existing hover/audio/variation behavior, silent
  missing-file handling, verified YouTube mapping, cancellation, global mute, file-mode
  fallback and visibility gating.
- Static website validation: 1,278 local references, matching navigation, unchanged
  script narrative and canon, 148 decoded PNGs and six JavaScript syntax checks.
- Local server returns HTTP 200 for the story and HTTP 206 for a 32-byte video range;
  it sends the cross-origin referrer policy needed by embedded playback.

## Scope

YouTube uploads are performed and verified through the signed-in in-app browser.
Per-video completion evidence is in `youtube-uploads.json`. Entries still marked
`pending` have not been completed; do not infer completion from their titles or
staging files. Earlier completed film uploads are reused with their current visibility.

Website browser interaction/visual QA has not been performed. YouTube fallback is
covered by static and isolated behavior checks; live embeds still depend on network
availability, browser autoplay policy and YouTube's availability and permissions.

## Ownership and size

The existing preview module keeps the single active preview, audio and selected-take
state. The separate YouTube adapter loads and controls the external player. The
upload catalog owns verified IDs and export metadata. The local server owns only
local HTTP delivery. No language, compiler, .NET application or runtime was changed.

The new repository deliberately includes the supplied/generated artwork and saved
workflow/history JSON. Those generated records are data, not application modules.
Every video remains excluded from Git. No new packages were installed.

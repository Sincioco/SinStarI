# Sin Star I — Storyboard Draft 3

This is the main working copy: **D:\SMILE 2.0 - Sin Star I\Visual Script and Storyboard**.
Changes are made directly here. ZIP exports are no longer part of routine updates.

Double-click **Start Website.cmd** to open the site in Chrome at
**http://localhost:8765/**. This uses the installed PowerShell and Windows .NET
components, with no package downloads. **Stop Website.cmd** stops the local server.
The server is local to this computer; it does not publish the website.

You can also open **[index.html](index.html)** directly for offline reading and local
video previews. Keep the folders together. Embedded YouTube playback requires the
local launcher (or another HTTP/HTTPS host) and an internet connection.

## Two views, one story

- **[Storyboard](index.html)** — 121 individual illustrations with dialogue.
- **[Script](Sin-Star-I-Game-Script-v0.2.html)** — the complete accepted script,
  with the game poster below its title, seven cast portraits, and illustrations
  placed at the matching story beats.
- Both views share the same header, chapter navigation, scene search, light/dark
  theme switch and Print control. Switching views keeps the current scene.
- The selected theme follows links between views, even when a browser restricts
  saved preferences for local files.
- **[Films & Trailer](movies.html)** retains the finished movies and their
  YouTube links. **[Canon](Canon.md)** retains the accepted decisions.

## Bring the pictures to life

Hover over a picture to play its LTX 2.5 animation. Move away to restore the
illustration. On a phone or with a keyboard, use **Play Preview**. Select it again
to stop. **Escape** also stops the preview.

Only one preview plays at a time. Clips load when requested, and playback stops
when the image goes offscreen or you leave the page. With reduced motion enabled
in your system, previews start only when you select Play Preview.

### Audio

Select **Audio Off** in the shared header to turn **Audio On**. The switch controls
all picture previews in both views and remembers your setting. Turning it off
mutes the current preview immediately. The original render soundtracks are included.

Your first visit starts with audio off. If the browser later requires a click
before playing sound, the preview continues muted and offers **Play With Sound**.
Select that button to hear it. Complete movies keep their own player controls.

### Clip Variations

Where a picture has multiple clips, select **Clip 1**, **Clip 2**, and so on beneath
the image. Your selection plays immediately and is used for subsequent hovers on
that page. Check **Remember** to keep the choice across Script and Storyboard,
including later visits. Uncheck it to stop saving that picture's selection.

Audio and remembered clip choices also travel in the view links, so switching
views works even when browser storage is restricted. Lasting preferences require
browser storage or reopening a link/bookmark that contains those choices.

Select an image in the Script to return to its matching Storyboard panel. The
poster returns to the beginning; cast portraits link to their story introductions.
Selecting a Storyboard image opens the full illustration.

In **Chapter 9, Scene 3**, **A World Hurled** shows Aevos throwing a planet at Arin
and the party. **Clips 1 and 2** preserve the earlier eight-second versions.
**Clips 3–7** are five new ten-second variations: the world strikes Mira's shield,
breaks apart, and the shield then fails as the party is forced back. **Clip 3** is
the default unless you have remembered another take. Dialogue and the same choices
appear in both views.

### YouTube and missing videos

Select **YouTube** below an uploaded picture to play the selected take in place.
Select **Stop YouTube** to return to the illustration. **Open on YouTube** opens
the same verified upload in a new tab and also works when you open HTML directly.

Hover playback tries the local MP4 first. If it is missing, the site uses the
matching verified YouTube upload when embedded playback is supported. If neither
is available, the illustration stays visible without an error message. Diagnostic
details go to the browser console. Audio, reduced motion and stopping on departure
also apply to the YouTube previews; browser autoplay rules may require a click.

YouTube controls appear only after an upload is verified. The current upload
inventory is in [production/youtube-uploads.json](production/youtube-uploads.json).
Video files are excluded from Git, so a fresh clone uses the uploaded versions.

## Movies

| Movie | Length | YouTube |
| --- | --- | --- |
| Defy the End — Cinematic Trailer | 30 seconds | [Watch](https://youtu.be/KSLICX-pJS0) |
| A Universe Worth Fighting For — Story Film | 4 minutes 38 seconds | [Watch](https://youtu.be/QiwCNI7RVLc) |
| Room for One — Opening Preview | 30 seconds | [Watch](https://youtu.be/iXHhrFC2W3o) |

The story film contains major spoilers. These are cinematic concept previews of
a game in development, animated from storyboard artwork with LTX 2.5.

**Created by: Louiery R. Sincioco (Sin)**

Sin Star is the first game project to use the new **SMILE Programming Language,
Compiler, Libraries and Tool Chain**.

**Open-source project:** https://github.com/sincioco/smile-2.0

## Files and earlier drafts

Images are in `asset/images`; complete movies are in `asset/videos`; 135 clips for
129 pictures are in `asset/videos/hover`. Both views reference the same media.
Hover filenames begin with their scene and picture title, for example
`C00-S01 - Close - Memory.mp4`. Variations use `_Clip2`, `_Clip3`, and so on.
Cast portraits and the poster use `CAST` and `POSTER` prefixes.
Original four-panel sheets remain in the image archive.

Drafts 1 and 2 remain unchanged in their original folders. This is the continuing
Draft 3 working website. Its movies retain the credited Draft 2 edits and sharing links.
The story film is packaged at 720p; the two short movies are 1080p.

The `production` folder keeps media mappings, source artwork, original render
copies, saved ComfyUI workflows, templates and validation evidence together.
The installed ComfyUI models, Python/Pillow and FFmpeg are authoring tools, not
website viewing requirements. See [Production Notes](production/README.md).

## Refresh

No .NET rebuild, VSIX installation or application restart is needed. Open this
Draft 3 edition. If replacing an already open copy, press **Ctrl+F5 in Chrome**.
Images, previews, styles and scripts use content versions to prevent stale assets.

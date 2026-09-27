"""Preserve the approved fight, replace only its retreat, and lock the next-shot pose."""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    fight = ROOT / 'asset/videos/hover/C00-S01_Clip4 - Wide - Moving Godlike.mp4'
    ending = ROOT / 'production/render-sources/godlike-teleport-ending-take1.mp4'
    target = ROOT / 'production/render-sources/godlike-teleport-finished.mp4'
    final_frame = HERE / 'references/next-first-frame.png'
    filters = (
        '[0:v]trim=end_frame=144,setpts=PTS-STARTPTS,setsar=1[fight];'
        '[1:v]trim=end_frame=144,setpts=PTS-STARTPTS,setsar=1[ending];'
        '[fight][ending]concat=n=2:v=1:a=0[joined];'
        '[2:v]scale=1280:720:flags=lanczos,format=rgba,'
        'fade=t=in:st=11.5:d=0.4166667:alpha=1[end];'
        '[joined][end]overlay=shortest=1:format=auto,format=yuv420p[v];'
        '[0:a]atrim=end=6,asetpts=PTS-STARTPTS[a0];'
        '[1:a]atrim=end=6,asetpts=PTS-STARTPTS[a1];'
        '[a0][a1]acrossfade=d=0.08,apad[a]'
    )
    subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-y',
        '-i', str(fight), '-i', str(ending), '-loop', '1', '-framerate', '24', '-i', str(final_frame),
        '-filter_complex', filters, '-map', '[v]', '-map', '[a]', '-t', '12', '-r', '24',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart', str(target)], check=True)
    print(target)


if __name__ == '__main__':
    main()

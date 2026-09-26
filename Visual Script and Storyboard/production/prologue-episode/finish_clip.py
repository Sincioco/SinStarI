"""Apply explicit, reviewed editorial corrections and accept a single clip."""
import argparse
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('shot')
    p.add_argument('--take', type=int, default=1)
    p.add_argument('--crop')
    p.add_argument('--fade-white', action='store_true')
    p.add_argument('--wordless', action='store_true')
    p.add_argument('--dream-bridge', action='store_true')
    p.add_argument('--alternate-only', action='store_true')
    p.add_argument('--review', required=True)
    p.add_argument('--scale', default='Wide')
    args = p.parse_args()
    identifier = f'episode-{args.shot}-take{args.take}'
    checks = json.loads((HERE / 'dialogue-review.json').read_text(encoding='utf-8'))
    entry = checks[identifier]
    source = ROOT / entry['file']
    target = source.with_name(identifier + '-finished.mp4')
    video = []
    if args.crop:
        video.append('crop=' + args.crop)
    video += [f'scale={entry["width"]}:{entry["height"]}:flags=lanczos', 'setsar=1']
    if args.fade_white:
        video.append(f'fade=t=out:st={entry["duration"] - 1.2}:d=1.0:color=white')
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source)]
    if args.wordless:
        # An inharmonic sound design cue replaces an unwanted model-invented word.
        command += ['-f', 'lavfi', '-i',
                    f'aevalsrc=0.10*sin(2*PI*146.83*t)+0.045*sin(2*PI*239.4*t)+0.03*sin(2*PI*401.7*t):s=48000:d={entry["duration"]}']
        command += ['-map', '0:v:0', '-map', '1:a:0', '-af',
                    f'afade=t=in:d=0.4,afade=t=out:st={entry["duration"]-1.3}:d=1.2,aecho=0.6:0.4:160|290:0.25|0.15']
    elif args.dream_bridge:
        command += ['-i', str(source.with_name('episode-unspoken-sound-take1.mp4')),
                    '-filter_complex', '[0:a]atrim=end=5.15,afade=t=out:st=4.8:d=0.35,apad[ambient];'
                    '[1:a]atrim=start=0.3:end=2.4,asetpts=PTS-STARTPTS,volume=0.55,'
                    'afade=t=in:d=0.2,afade=t=out:st=1.7:d=0.4,adelay=4800|4800[echo];'
                    '[ambient][echo]amix=inputs=2:duration=longest:normalize=0[audio]',
                    '-map', '0:v:0', '-map', '[audio]']
    command += ['-vf', ','.join(video), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-t', str(entry['duration']),
                '-movflags', '+faststart', str(target)]
    if args.crop or args.fade_white or args.wordless or args.dream_bridge:
        subprocess.run(command, check=True)
        final = target
    else:
        final = source
    accepted_path = HERE / 'accepted.json'
    accepted = json.loads(accepted_path.read_text(encoding='utf-8'))
    key = identifier + '-bridge' if args.dream_bridge else identifier
    accepted[key] = dict(shot=args.shot, file=final.relative_to(ROOT).as_posix(),
        review=args.review, scale=args.scale, original=source.relative_to(ROOT).as_posix(),
        video_filter=','.join(video), wordless_sound_design=args.wordless,
        dream_bridge=args.dream_bridge, episode_use=not args.alternate_only)
    accepted_path.write_text(json.dumps(accepted, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(identifier + ': reviewed and prepared')


if __name__ == '__main__':
    main()

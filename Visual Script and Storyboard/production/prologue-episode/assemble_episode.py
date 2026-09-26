"""Assemble reviewed prologue takes, preserving exact dialogue and a 2s 4K poster."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / 'production/local-state/prologue-episode/assembly'


def run(args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + args,
                   cwd=ROOT, check=True)


def encoding(seconds, target):
    return ['-t', str(seconds), '-r', '24', '-c:v', 'h264_nvenc', '-preset', 'p6',
            '-cq', '18', '-b:v', '0', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
            '-ar', '48000', '-ac', '2', '-b:a', '192k', '-movflags', '+faststart', str(target)]


def text_card(name, lines, seconds):
    filters = []
    for index, (line, size, y) in enumerate(lines):
        path = WORK / f'{name}-{index}.txt'
        path.write_text(line, encoding='utf-8')
        relative = path.relative_to(ROOT).as_posix()
        filters.append(f"drawtext=fontfile='C\\:/Windows/Fonts/georgia.ttf':textfile='{relative}':"
                       f'fontcolor=0xead8ad:fontsize={size}:x=(w-text_w)/2:y={y}')
    target = WORK / (name + '.mp4')
    run(['-f', 'lavfi', '-i', 'color=c=0x081322:s=3840x2160:r=24', '-f', 'lavfi',
         '-i', 'anullsrc=r=48000:cl=stereo', '-vf', ','.join(filters)] + encoding(seconds, target))
    return target


def main():
    config = json.loads((HERE / 'episode.json').read_text(encoding='utf-8'))
    accepted = json.loads((HERE / 'accepted.json').read_text(encoding='utf-8'))
    chosen = {entry['shot']: (identifier, entry) for identifier, entry in accepted.items()
              if entry.get('episode_use', True)}
    WORK.mkdir(parents=True, exist_ok=True)
    poster = WORK / '00-poster.mp4'
    run(['-loop', '1', '-framerate', '24', '-i', str(ROOT / config['poster_source']),
         '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-vf',
         'scale=3840:2160:flags=lanczos,setsar=1'] + encoding(2, poster))
    opening = WORK / '01-black-rattle.mp4'
    rattle = ('aevalsrc=0.045*sin(2*PI*1700*t)*exp(-28*mod(t\\,0.19))+'
              '0.024*sin(2*PI*2317*t)*exp(-20*mod(t\\,0.19)):s=48000:d=0.75')
    run(['-f', 'lavfi', '-i', 'color=c=black:s=3840x2160:r=24', '-f', 'lavfi', '-i', rattle]
        + encoding(0.75, opening))
    parts = [poster, opening]
    timeline = [dict(id='poster', start=0, seconds=2), dict(id='black-rattle', start=2, seconds=0.75)]
    cursor = 2.75
    for index, shot in enumerate(config['shots']):
        if 'reuse' in shot:
            source, identifier = ROOT / shot['reuse'], shot['id']
            start = shot.get('start', 0)
            seconds = round(shot['seconds'] * 24) / 24
        else:
            identifier, entry = chosen[shot['id']]
            source, start = ROOT / entry['video'], 0
            probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format',
                                '-of', 'json', str(source)], text=True))
            seconds = round(float(probe['format']['duration']) * 24) / 24
        target = WORK / f'{index+2:02d}-{shot["id"]}.mp4'
        vf = 'scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,crop=3840:2160,setsar=1'
        af = 'aresample=48000,apad,alimiter=limit=0.95:level=0'
        run(['-ss', str(start), '-i', str(source), '-vf', vf, '-af', af] + encoding(seconds, target))
        parts.append(target)
        timeline.append(dict(id=identifier, shot=shot['id'], start=cursor, seconds=seconds,
                             source=source.relative_to(ROOT).as_posix(), dialogue=shot['dialogue']))
        cursor += seconds
        print(f'{index+1}/{len(config["shots"])} {shot["id"]}', flush=True)
    title = text_card('title', [('SIN STAR I', 210, 850), ('PROLOGUE  ·  ROOM FOR ONE', 64, 1170)], 3)
    creator = text_card('creator', [('Created by: Louiery R. Sincioco (Sin)', 110, 990)], 4)
    project = text_card('project', [
        ('Sin Star is the first game project to use the new', 86, 690),
        ('SMILE Programming Language, Compiler,', 86, 835),
        ('Libraries and Tool Chain', 86, 980),
        ('Open-source project', 74, 1250),
        ('https://github.com/sincioco/smile-2.0', 74, 1370)], 7)
    parts += [title, creator, project]
    timeline += [dict(id='title', start=cursor, seconds=3),
                 dict(id='creator', start=cursor+3, seconds=4),
                 dict(id='project', start=cursor+7, seconds=7)]
    manifest = WORK / 'concat.txt'
    manifest.write_text('\n'.join("file '" + p.as_posix().replace("'", "'\\''") + "'" for p in parts), encoding='utf-8')
    output = ROOT / config['output']
    # Re-clock concatenated frames so the poster occupies exactly frames 0..47;
    # independent AAC encoders otherwise leave tiny timestamp offsets per cut.
    run(['-f', 'concat', '-safe', '0', '-i', str(manifest), '-vf', 'setpts=N/(24*TB)',
         '-af', 'asetpts=N/SR/TB'] + encoding(round((cursor + 14) * 24) / 24, output))
    (HERE / 'episode-timeline.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(output), flush=True)


if __name__ == '__main__':
    main()

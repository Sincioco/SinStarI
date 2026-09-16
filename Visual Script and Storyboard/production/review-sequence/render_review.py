"""Build an ordered, labeled review movie from an editable JSON sequence."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
from review_art import overlay, poster, credits
from review_media import MediaRunner, duration, encoding, probe

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'production/local-state/review-sequence'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(status, percent, phase, **extra):
    value = dict(status=status, percent=round(percent, 1), phase=phase, pid=os.getpid(), **extra)
    temporary = CACHE / 'progress.tmp'
    temporary.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
    # Windows readers and antivirus may briefly hold the previous snapshot.
    for attempt in range(20):
        try:
            temporary.replace(CACHE / 'progress.json')
            break
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.025)


def concatenate_files(paths, segments, target):
    target.write_text(''.join("file '" + str(p.resolve()).replace('\\', '/').replace("'", "'\\''")
                              + f"'\nduration {segment['seconds']:.9f}\n"
                              for p, segment in zip(paths, segments)), encoding='utf-8')


def render(config_path, prepare_only=False):
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes.decode('utf-8-sig'))
    config_hash = hashlib.sha256(config_bytes).hexdigest()
    layout = config['settings'].get('layout', 'overlay')
    if layout not in ('overlay', 'side-by-side'):
        raise ValueError('layout must be overlay or side-by-side')
    if config['settings'].get('show_labels', True) is False:
        layout = 'overlay'
    for key in ('clip_volume', 'music_volume', 'master_volume'):
        if not 0 <= float(config['audio'][key]) <= 2:
            raise ValueError(key + ' must be between 0.0 (mute) and 2.0 (double amplitude)')
    entries = [item for item in config['clips'] if item.get('enabled', True)]
    if not entries or len({x['id'] for x in entries}) != len(entries):
        raise ValueError('The sequence needs clips with unique IDs')
    fps = int(config['settings']['fps'])
    if fps not in (24, 25, 30, 48, 50, 60):
        raise ValueError('Unsupported frame rate')
    output = (ROOT / config['output']).resolve()
    output.relative_to(ROOT)  # Keep generated movie ownership in this website.
    sources = [(ROOT / x['file']).resolve() for x in entries]
    tracks = [(ROOT / x).resolve() for x in config['music']['files']]
    for path in sources + tracks + [ROOT / config['opening']['image'],
                                   ROOT / config['credits']['background'], ROOT / config['credits']['logo']]:
        if not path.is_file():
            raise FileNotFoundError(path)
        if path == output:
            raise ValueError('Output must not overwrite an input')
    poster(ROOT / config['opening']['image'], CACHE / 'opening.png')
    credits(ROOT, config['credits'], CACHE / 'credits.png')
    segments = [dict(id='opening', still=CACHE / 'opening.png',
                     seconds=float(config['opening']['seconds']), title='Sin Star I · Game Poster')]
    cursor = segments[0]['seconds']
    timeline = []
    for index, (entry, source) in enumerate(zip(entries, sources)):
        report('running', 0, f'Preparing labels and timing {index + 1}/{len(entries)}')
        native = duration(source)
        start = float(entry.get('start_seconds', 0))
        seconds = float(entry.get('duration_seconds', native - start))
        if start < 0 or seconds <= 0 or start + seconds > native + 1 / fps:
            raise ValueError('Invalid trim: ' + entry['id'])
        seconds = math.ceil(seconds * fps - 0.001) / fps
        label = CACHE / f'label-{index:03d}.png'
        overlay(entry, index + 1, len(entries), label, config)
        title = entry['scene'] + ' · ' + entry['scene_title']
        if entry.get('take'):
            title += ' · ' + entry['take']
        segments.append(dict(id=entry['id'], source=source, overlay=label,
                             seconds=seconds, start=start, title=title, muted=entry.get('muted') is True, layout=layout))
        timeline.append(dict(number=index + 1, id=entry['id'], start_seconds=round(cursor, 3),
                             end_seconds=round(cursor + seconds, 3), chapter=entry['chapter'],
                             scene=entry['scene'], title=entry['scene_title'], file=entry['file']))
        cursor += seconds
    segments.append(dict(id='credits', still=CACHE / 'credits.png',
                         seconds=float(config['credits']['seconds']), title='Credits · Created by Louiery R. Sincioco (Sin)'))
    total = sum(s['seconds'] for s in segments)
    timeline_path = config_path.with_name(config_path.stem + '-timeline.csv')
    with timeline_path.open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=timeline[0].keys())
        writer.writeheader()
        writer.writerows(timeline)
    if prepare_only:
        report('prepared', 100, f'{len(entries)} clips; {total:.2f} seconds', output=str(output))
        print(json.dumps(dict(clips=len(entries), seconds=total, timeline=str(timeline_path))))
        return
    runner = MediaRunner(CACHE, report)
    codec = encoding(config['settings']['encoder'])
    outputs = []
    elapsed = 0
    for index, segment in enumerate(segments):
        fingerprint = dict(segment={k:str(v) for k,v in segment.items()}, fps=fps,
                           codec=codec, segment_format='mov-pcm-v1')
        for key in ('source', 'overlay', 'still'):
            if key in segment:
                fingerprint[key + '_sha256'] = digest(segment[key])
        identity = hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()[:20]
        target = CACHE / (identity + '.mov')
        seconds = segment['seconds']
        if not target.exists():
            temporary = CACHE / (identity + '-building.mov')
            if 'still' in segment:
                inputs = ['-loop', '1', '-framerate', str(fps), '-i', segment['still'],
                          '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
                filters = '[0:v]setsar=1,format=yuv420p[v];[1:a]anull[a]'
            else:
                inputs = ['-ss', str(segment['start']), '-i', segment['source'],
                          '-loop', '1', '-framerate', str(fps), '-i', segment['overlay']]
                frame_width = 1344 if segment['layout'] == 'side-by-side' else 1920
                filters = (f'[0:v]fps={fps},scale={frame_width}:1080:force_original_aspect_ratio=decrease,'
                           f'pad={frame_width}:1080:(ow-iw)/2:(oh-ih)/2:color=0x070e1b,'
                           'pad=1920:1080:0:0:color=0x070e1b,setsar=1,'
                           'tpad=stop_mode=clone:stop_duration=1[base];'
                           '[base][1:v]overlay=0:0,format=yuv420p[v];')
                has_audio = any(s['codec_type'] == 'audio' for s in probe(segment['source'])['streams'])
                if has_audio:
                    mute = ',volume=0' if segment['muted'] else ''
                    filters += '[0:a]aresample=48000,aformat=channel_layouts=stereo,apad' + mute + '[a]'
                else:
                    inputs += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
                    filters += '[2:a]anull[a]'
            runner.run(inputs + ['-filter_complex', filters, '-map', '[v]', '-map', '[a]',
                                 '-t', str(seconds), '-r', str(fps), *codec, '-pix_fmt', 'yuv420p',
                                 '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2',
                                 '-video_track_timescale', str(fps * 1000), temporary],
                       seconds, 85 * elapsed / total, 85 * seconds / total,
                       f'Rendering {index + 1}/{len(segments)} · {segment["title"]}')
            temporary.replace(target)
        outputs.append(target)
        elapsed += seconds
        report('running', 85 * elapsed / total, f'Prepared {index + 1}/{len(segments)} segments')
    concatenate_files(outputs, segments, CACHE / 'concat.txt')
    runner.run(['-f', 'concat', '-safe', '0', '-i', CACHE / 'concat.txt', '-c', 'copy',
                CACHE / 'assembled.mov'], total, 85, 3, 'Joining the ordered clips')
    crossfade = float(config['music']['crossfade_seconds'])
    track_lengths = [duration(path) for path in tracks]
    if not 0 < crossfade < min(track_lengths) / 2:
        raise ValueError('Music crossfade must be positive and shorter than half a track')
    chosen, music_seconds, track_starts = [], 0, []
    while music_seconds < total + crossfade:
        i = len(chosen) % len(tracks)
        track_starts.append(dict(file=str(tracks[i].relative_to(ROOT)),
                                 start_seconds=round(max(0, music_seconds - crossfade), 3)))
        music_seconds += track_lengths[i] - (crossfade if chosen else 0)
        chosen.append(tracks[i])
    audio_inputs, filters = [], []
    for i, path in enumerate(chosen):
        audio_inputs += ['-i', path]
        filters.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo[m{i}]')
    previous = 'm0'
    for i in range(1, len(chosen)):
        filters.append(f'[{previous}][m{i}]acrossfade=d={crossfade}:c1=qsin:c2=qsin[x{i}]')
        previous = f'x{i}'
    filters.append(f'[{previous}]atrim=duration={total},'
                   f'afade=t=out:st={max(0,total-3)}:d=3[music]')
    runner.run(audio_inputs + ['-filter_complex', ';'.join(filters), '-map', '[music]',
                               '-c:a', 'pcm_s16le', CACHE / 'music.wav'],
               total, 88, 4, 'Crossfading the three music tracks in sequence')
    metadata = [';FFMETADATA1', 'title=Sin Star I - Story Video Sequence Review',
                'artist=Louiery R. Sincioco (Sin)']
    cursor = 0
    for segment in segments:
        safe_title = segment['title'].replace('=', r'\=').replace(';', r'\;').replace('#', r'\#')
        metadata += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={round(cursor*1000)}',
                     f'END={round((cursor+segment["seconds"])*1000)}', 'title=' + safe_title]
        cursor += segment['seconds']
    (CACHE / 'chapters.txt').write_text('\n'.join(metadata) + '\n', encoding='utf-8')
    mix = (f'[0:a]volume={config["audio"]["clip_volume"]}[clip];'
           f'[1:a]volume={config["audio"]["music_volume"]}[music];'
           '[clip][music]amix=inputs=2:duration=longest:normalize=0,'
           f'volume={config["audio"]["master_volume"]},alimiter=limit=0.95:level=0[a]')
    runner.run(['-i', CACHE / 'assembled.mov', '-i', CACHE / 'music.wav', '-i', CACHE / 'chapters.txt',
                '-filter_complex', mix,
                '-map', '0:v:0', '-map', '[a]', '-map_metadata', '2', '-map_chapters', '2',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-t', str(total),
                '-movflags', '+faststart', CACHE / 'finished.mp4'], total, 92, 7, 'Writing the review movie and chapter markers')
    result = probe(CACHE / 'finished.mp4')
    actual = float(result['format']['duration'])
    if abs(actual - total) > 0.15:
        raise RuntimeError(f'Unexpected final duration: {actual} versus {total}')
    output.parent.mkdir(parents=True, exist_ok=True)
    (CACHE / 'finished.mp4').replace(output)
    receipt = dict(status='Rendered', rendered_at=datetime.now(timezone.utc).isoformat(),
                   output=str(output.relative_to(ROOT)), sha256=digest(output), clips=len(entries),
                   seconds=actual, dimensions='1920x1080', fps=fps, encoder=codec[1],
                   opening_seconds=config['opening']['seconds'], credits_seconds=config['credits']['seconds'],
                   audio=config['audio'], music_tracks=track_starts,
                   music_crossfade_seconds=crossfade, timeline=str(timeline_path.relative_to(ROOT)),
                   layout=layout, muted_clips=[x['id'] for x in entries if x.get('muted') is True],
                   panel_positions={x['id']:x['panel_positions'] for x in entries if 'panel_positions' in x},
                   config_sha256=config_hash)
    config_path.with_name(config_path.stem + '-render.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    phase = 'Review movie ready' if digest(config_path) == config_hash else 'Movie ready from render-start settings; JSON has newer edits. Render again to include them.'
    report('complete', 100, phase, output=str(output))
    print(json.dumps(receipt))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=Path(__file__).with_name('sequence.json'))
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    lock = CACHE / 'render.lock'
    try:
        handle = lock.open('x')
    except FileExistsError:
        raise SystemExit('A render owns render.lock. Check its process before removing a stale lock.')
    try:
        with handle:
            handle.write(str(os.getpid()))
        (CACHE / 'cancel.request').unlink(missing_ok=True)
        render(args.config.resolve(), args.prepare_only)
    except (Exception, KeyboardInterrupt) as error:
        report('cancelled' if isinstance(error, KeyboardInterrupt) else 'failed', 0, str(error))
        raise
    finally:
        lock.unlink(missing_ok=True)


if __name__ == '__main__':
    main()

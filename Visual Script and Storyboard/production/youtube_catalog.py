"""Prepare upload metadata and record only UI-verified YouTube results."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from media_catalog import all_clips

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'production/youtube-uploads.json'
DESCRIPTION = ('Created by: Louiery R. Sincioco (Sin)\n\n'
    'Sin Star is the first game project to use the new SMILE Programming Language, '
    'Compiler, Libraries and Tool Chain.\n\n'
    'Open-source game and storyboard: https://github.com/sincioco/SinStarI\n'
    'SMILE compiler and tool chain: https://github.com/sincioco/smile-2.0\n\n'
    'AI-generated cinematic concept animation rendered with LTX 2.5. Game in development.')

def read():
    return json.loads(REGISTRY.read_text(encoding='utf-8')) if REGISTRY.exists() else []

def write(entries):
    REGISTRY.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    verified = {entry['id']:entry['youtube_id'] for entry in entries
                if entry['status'] == 'uploaded' and re.fullmatch(r'[A-Za-z0-9_-]{11}', entry.get('youtube_id', ''))}
    (ROOT / 'asset/youtube-uploads.js').write_text(
        '/* Generated from verified production/youtube-uploads.json records. */\n'
        'window.SinStarUploads = Object.freeze(' + json.dumps(verified, ensure_ascii=False, indent=2) + ');\n',
        encoding='utf-8')
    version = hashlib.sha256((ROOT / 'asset/youtube-uploads.js').read_bytes()).hexdigest()[:10]
    for page in ROOT.glob('*.html'):
        source = page.read_text(encoding='utf-8')
        updated = re.sub(r'asset/youtube-uploads\.js\?v=[^"\s]+', 'asset/youtube-uploads.js?v=' + version, source)
        if source != updated:
            page.write_text(updated, encoding='utf-8')

def prepare():
    previous = {entry['id']:entry for entry in read()}
    items = json.loads((ROOT / 'production/hover-media.json').read_text(encoding='utf-8'))
    entries = []
    for clip in all_clips(items):
        entry = previous.get(clip['id'], dict(id=clip['id'], status='pending'))
        entry.update(file=clip['video'], title=clip['youtube_title'],
                     description=clip['caption'] + '\n\n' + DESCRIPTION)
        path = ROOT / clip['video']
        if path.is_file():
            entry['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(entry)
    entries += [entry for entry in previous.values() if entry.get('kind') == 'film']
    write(entries)
    return entries

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', nargs=2, metavar=('CLIP_ID', 'YOUTUBE_ID'))
    parser.add_argument('--visibility', default='unlisted', choices=['unlisted','public'])
    parser.add_argument('--stage', type=int, default=0)
    parser.add_argument('--planet-first', action='store_true')
    args = parser.parse_args()
    entries = prepare()
    if args.record:
        identifier, video_id = args.record
        assert re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id)
        entry = next(x for x in entries if x['id'] == identifier)
        assert 'sha256' in entry
        entry.update(status='uploaded', youtube_id=video_id, url='https://youtu.be/' + video_id,
                     visibility=args.visibility, verified_at=datetime.now(timezone.utc).isoformat(),
                     verified_via='YouTube Studio UI')
        write(entries)
    if args.stage:
        folder = ROOT / 'production/local-state/upload-batch'
        folder.mkdir(parents=True, exist_ok=True)
        batch = []
        ordered = sorted(entries, key=lambda x: not x['id'].startswith('new-c09-s03-planet')) if args.planet_first else entries
        for entry in ordered:
            source = ROOT / entry['file']
            if entry['status'] != 'pending' or not source.exists():
                continue
            name = re.sub(r'[<>:"/\\|?*]', '-', entry['title']) + '.mp4'
            target = folder / name
            if not target.exists():
                target.hardlink_to(source)
            batch.append(dict(id=entry['id'], title=entry['title'], path=str(target)))
            if len(batch) == args.stage:
                break
        (ROOT / 'production/local-state/current-upload-batch.json').write_text(
            json.dumps(batch, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(batch, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(dict(total=len(entries), uploaded=sum(x['status']=='uploaded' for x in entries))))

if __name__ == '__main__':
    main()

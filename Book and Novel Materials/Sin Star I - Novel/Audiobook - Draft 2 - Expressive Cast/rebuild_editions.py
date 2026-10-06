"""Combine the accepted chapter MP3s with local FFmpeg; no TTS or network access."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result


def escape_metadata(text):
    return str(text).replace('\\', '\\\\').replace('\n', ' ').replace('=', '\\=').replace(';', '\\;').replace('#', '\\#')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--formats', nargs='+', choices=['mp3', 'm4b', 'mobile'], default=['mp3', 'm4b'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'release-manifest.json').read_text(encoding='utf-8'))
    config = json.loads((root / 'chapter-metadata-defaults.json').read_text(encoding='utf-8'))
    chapters = manifest['chapters']
    assert len(chapters) == manifest['sections'] and len(chapters) > 0
    files = []
    durations = []
    for index, chapter in enumerate(chapters):
        path = (root / chapter['file']).resolve()
        assert path.parent == root and chapter['index'] == index
        assert hashlib.sha256(path.read_bytes()).hexdigest() == chapter['mp3_sha256'], path.name + ' checksum mismatch'
        probe = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)]).stdout)
        files.append(path)
        durations.append(float(probe['format']['duration']))
    if args.verify_only:
        print(json.dumps({'verified_chapters': len(files), 'encoded_duration_seconds': sum(durations)}))
        return
    output = args.output.resolve() if args.output else root / 'rebuilt-editions'
    output.mkdir(parents=True, exist_ok=True)
    title = ' - '.join(x for x in (config['title_base'], config.get('draft_label')) if x)
    stem = ''.join(c for c in title if c not in '<>:"/\\|?*') + ' - Rebuilt Complete Audiobook'
    paths = {kind: output / (stem + (' - Mobile.mp3' if kind == 'mobile' else '.' + kind)) for kind in args.formats}
    for path in paths.values():
        if path.exists():
            raise FileExistsError('Refusing to overwrite ' + str(path))
    with tempfile.TemporaryDirectory(prefix='sin-star-assembly-') as temporary:
        temp = Path(temporary)
        concat = temp / 'chapters.txt'
        concat.write_text(''.join("file '" + p.as_posix().replace("'", "'\\''") + "'\n" for p in files), encoding='utf-8')
        metadata = [';FFMETADATA1', 'title=' + escape_metadata(title), 'artist=' + escape_metadata(config['artist']), 'album=' + escape_metadata(config['album'])]
        offset = 0.0
        for chapter, duration in zip(chapters, durations):
            metadata.extend(['[CHAPTER]', 'TIMEBASE=1/1000', f'START={round(offset * 1000)}', f'END={round((offset + duration) * 1000)}', 'title=' + escape_metadata(chapter['heading'])])
            offset += duration
        meta = temp / 'chapters.ffmetadata'
        meta.write_text('\n'.join(metadata) + '\n', encoding='utf-8')
        records = []
        for kind, destination in paths.items():
            # The unfinished output stays separate until FFprobe validates it.
            staged = destination.with_name(destination.stem + '.partial' + destination.suffix)
            codec = ['-c:a', 'copy'] if kind == 'mp3' else ['-c:a', 'aac' if kind == 'm4b' else 'libmp3lame', '-b:a', '96k' if kind == 'm4b' else '32k']
            command = ['ffmpeg', '-v', 'error', '-n', '-f', 'concat', '-safe', '0', '-i', str(concat), '-i', str(meta), '-map', '0:a:0', '-map_metadata', '1', '-map_chapters', '1', *codec]
            if kind == 'm4b':
                command += ['-movflags', '+faststart', '-f', 'mp4']
            run(command + [str(staged)])
            probe = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:chapter', '-of', 'json', str(staged)]).stdout)
            assert abs(float(probe['format']['duration']) - sum(durations)) < max(3, len(files) * 0.1)
            if kind == 'm4b':
                assert len(probe['chapters']) == len(chapters)
            staged.rename(destination)
            records.append({'file': destination.name, 'bytes': destination.stat().st_size, 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(), 'duration_seconds': float(probe['format']['duration']), 'chapter_markers': len(probe.get('chapters', []))})
            print('READY ' + str(destination), flush=True)
        (output / 'rebuild-report.json').write_text(json.dumps({'source_sha256': manifest['source_sha256'], 'input_chapters': len(chapters), 'input_hashes_verified': True, 'outputs': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

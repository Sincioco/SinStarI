"""Check the delivered episode's streams and independently transcribe each cut."""
import json
from pathlib import Path
import re
import subprocess
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT / 'production/local-state/prologue-episode/audio-check'


def normalize(text):
    text = text.lower().replace('nerys', 'neris').replace('nerris', 'neris')
    # Route is correctly pronounced either "root" or "rout". ASR alternates
    # spellings for the same checked source audio; keep this exception specific.
    text = text.replace('root recorder', 'route recorder').replace('root is unsafe', 'route is unsafe')
    text = re.sub(r'\bno{2,}\b', 'no', text)  # The requested nightmare scream elongates the vowel.
    return re.sub('[^a-z0-9]', '', text)


def main():
    config = json.loads((HERE / 'episode.json').read_text(encoding='utf-8'))
    timeline = json.loads((HERE / 'episode-timeline.json').read_text(encoding='utf-8'))
    video = ROOT / config['output']
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                              '-show_format', '-of', 'json', str(video)], text=True))
    stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    assert (stream['width'], stream['height']) == (3840, 2160)
    assert stream['r_frame_rate'] == '24/1'
    assert float(stream['start_time']) == 0
    assert any(s['codec_type'] == 'audio' for s in probe['streams'])
    model = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=8,
                         download_root=r'D:\AI\_cache\whisper')
    WORK.mkdir(exist_ok=True)
    result = dict(width=stream['width'], height=stream['height'], fps=24,
                  duration=float(probe['format']['duration']), poster_frames=48, dialogue=[])
    for item in timeline:
        if not item.get('dialogue'):
            continue
        path = WORK / (item['id'] + '.wav')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss',
            str(item['start']), '-i', str(video), '-t', str(item['seconds']), '-vn',
            '-ar', '16000', '-ac', '1', str(path)], check=True)
        # Whisper can omit a sustained scream when decoding it together with
        # ordinary speech. Check the two audible sections independently.
        sections = [(0, 7), (7, item['seconds'])] if item.get('shot') == 'wake' else [(0, item['seconds'])]
        spoken = []
        for number, (start, end) in enumerate(sections):
            section = path.with_name(path.stem + f'-{number}.wav')
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                '-ss', str(start), '-i', str(path), '-t', str(end - start), str(section)], check=True)
            segments, _ = model.transcribe(str(section), language='en', beam_size=5,
                                            condition_on_previous_text=False)
            spoken.extend(s.text.strip() for s in segments)
        actual = ' '.join(spoken)
        expected = ' '.join(line for _, line in item['dialogue'])
        record = dict(id=item['id'], expected=expected, actual=actual,
                      matches=normalize(expected) == normalize(actual))
        result['dialogue'].append(record)
        (HERE / 'episode-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(record), flush=True)
    assert all(r['matches'] for r in result['dialogue']), 'Inspect dialogue mismatches before delivery.'


if __name__ == '__main__':
    main()

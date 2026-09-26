"""Collect completed ComfyUI shots and independently transcribe their audio."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.request
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = Path(r'D:\Sin - AI Prompt\work\comfy_photo_video_output')
SOURCES = ROOT / 'production/render-sources/prologue-episode'
CONTACTS = ROOT / 'production/local-state/prologue-episode'


def normalized(text):
    return re.sub(r'[^a-z0-9]', '', text.lower().replace('’', "'"))


def main():
    model = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=8,
                         download_root=r'D:\AI\_cache\whisper')
    SOURCES.mkdir(parents=True, exist_ok=True)
    record = HERE / 'dialogue-review.json'
    results = json.loads(record.read_text(encoding='utf-8')) if record.exists() else {}
    while True:
        for receipt in HERE.glob('shots/*-receipt.json'):
            job = json.loads(receipt.read_text(encoding='utf-8'))
            identifier = job['id']
            if identifier in results:
                continue
            with urllib.request.urlopen('http://127.0.0.1:8191/history/' + job['prompt_id'], timeout=30) as response:
                history = json.load(response).get(job['prompt_id'])
            if not history:
                continue
            if history['status']['status_str'] != 'success':
                print(identifier + ': render failed; inspect history', flush=True)
                continue
            outputs = history.get('outputs', {}).get('901', {})
            files = outputs.get('images', outputs.get('gifs', []))
            if not files:
                files = [dict(filename=p.name, subfolder='SinStarI_PrologueEpisode')
                         for p in (OUTPUT / 'SinStarI_PrologueEpisode').glob(identifier + '_*.mp4')]
            source = OUTPUT / files[0]['subfolder'] / files[0]['filename']
            target = SOURCES / (identifier + '.mp4')
            shutil.copy2(source, target)
            probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                '-show_format', '-of', 'json', str(target)], text=True))
            video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            assert video['width'] * 9 == video['height'] * 16
            item = json.loads(receipt.with_name(identifier + '.json').read_text(encoding='utf-8'))
            segments, _ = model.transcribe(str(target), language='en', beam_size=5,
                                            condition_on_previous_text=False)
            segments = [dict(start=s.start, end=s.end, text=s.text.strip()) for s in segments]
            actual = ' '.join(s['text'] for s in segments)
            expected = ' '.join(s['text'] for s in item['dialogue'])
            result = dict(file=str(target.relative_to(ROOT)).replace('\\', '/'),
                          expected=expected, actual=actual, segments=segments,
                          spoken_text_matches=normalized(expected) == normalized(actual),
                          visual_review='pending', width=video['width'], height=video['height'],
                          duration=float(probe['format']['duration']))
            duration = result['duration']
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(target),
                '-vf', f'fps=5/{duration},scale=480:-1,tile=3x2', '-frames:v', '1',
                str(CONTACTS / (identifier + '.jpg'))], check=True)
            results[identifier] = result
            record.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(dict(id=identifier, expected=expected, actual=actual,
                                  matches=result['spoken_text_matches'])), flush=True)
        time.sleep(5)


if __name__ == '__main__':
    main()

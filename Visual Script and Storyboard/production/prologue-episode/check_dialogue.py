"""Transcribe actual audio with the existing local Faster Whisper runtime."""
import argparse
import json
from pathlib import Path
from faster_whisper import WhisperModel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--vad', action='store_true', help='Filter non-speech when checking quiet or wordless scenes.')
    args = parser.parse_args()
    model = WhisperModel('small.en', device='cpu', compute_type='int8',
                         download_root=r'D:\AI\_cache\whisper', cpu_threads=8)
    results = []
    for path in args.files:
        segments, info = model.transcribe(str(path), language='en', beam_size=5,
                                          condition_on_previous_text=False, vad_filter=args.vad)
        words = [dict(start=s.start, end=s.end, text=s.text.strip()) for s in segments]
        result = dict(file=str(path), segments=words,
                      text=' '.join(s['text'] for s in words))
        results.append(result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()

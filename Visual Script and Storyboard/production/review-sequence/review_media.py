"""FFmpeg process, progress and media probing for the review renderer."""
import json
import subprocess
from pathlib import Path

HIDDEN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                             '-of', 'json', str(path)], capture_output=True, text=True,
                            encoding='utf-8', check=True, creationflags=HIDDEN)
    return json.loads(result.stdout)


def duration(path):
    data = probe(path)
    video = next((x for x in data['streams'] if x['codec_type'] == 'video'), {})
    return float(video.get('duration', data['format']['duration']))


def encoding(requested):
    if requested == 'auto':
        trial = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                                'color=s=64x64:r=24', '-t', '0.1', '-c:v', 'h264_nvenc',
                                '-f', 'null', '-'], capture_output=True, creationflags=HIDDEN)
        requested = 'h264_nvenc' if trial.returncode == 0 else 'libx264'
    if requested == 'h264_nvenc':
        return ['-c:v', 'h264_nvenc', '-preset', 'p4', '-rc', 'vbr', '-cq', '20', '-b:v', '0']
    if requested != 'libx264':
        raise ValueError('encoder must be auto, h264_nvenc or libx264')
    return ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-threads', '8']


class MediaRunner:
    def __init__(self, cache, report):
        self.cache, self.report = cache, report

    def run(self, args, seconds, start_percent, span, phase):
        self.report('running', start_percent, phase)
        with (self.cache / 'ffmpeg.log').open('a', encoding='utf-8') as log:
            process = subprocess.Popen(['ffmpeg', '-hide_banner', '-y', '-nostats',
                                        '-loglevel', 'warning', '-stats_period', '0.5',
                                        '-progress', 'pipe:1', *map(str, args)],
                                       stdout=subprocess.PIPE, stderr=log, text=True,
                                       encoding='utf-8', creationflags=HIDDEN)
            try:
                for line in process.stdout:
                    if (self.cache / 'cancel.request').exists():
                        raise KeyboardInterrupt('Cancelled by reviewer')
                    if line.startswith('out_time_us='):
                        value = line.strip().split('=', 1)[1]
                        if value != 'N/A':
                            fraction = min(1, max(0, int(value) / 1_000_000 / seconds))
                            self.report('running', start_percent + span * fraction, phase)
                if process.wait():
                    raise RuntimeError('FFmpeg failed; see ' + str(self.cache / 'ffmpeg.log'))
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait()

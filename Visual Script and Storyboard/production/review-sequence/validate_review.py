"""Focused artifact checks, including the audio-join timestamp regression."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import ctypes
import threading
import time
import tempfile
import render_review
from review_media import probe

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name('sequence.json')


def progress_sharing_regression():
    """An ordinary Windows reader must not abort a render's progress update."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                                  ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    previous_cache = render_review.CACHE
    with tempfile.TemporaryDirectory() as temporary:
        try:
            render_review.CACHE = Path(temporary)
            render_review.report('running', 0, 'before lock')
            path = render_review.CACHE / 'progress.json'
            handle = kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0, None)
            assert handle != ctypes.c_void_p(-1).value
            def release():
                time.sleep(0.08)
                kernel.CloseHandle(handle)
            reader = threading.Thread(target=release)
            reader.start()
            render_review.report('complete', 100, 'after lock')
            reader.join()
            assert json.loads(path.read_text())['phase'] == 'after lock'
        finally:
            render_review.CACHE = previous_cache


def main():
    progress_sharing_regression()
    settings = json.loads(CONFIG.read_text(encoding='utf-8'))
    entries = [x for x in settings['clips'] if x.get('enabled', True)]
    movie = ROOT / settings['output']
    receipt = json.loads(CONFIG.with_name('sequence-render.json').read_text(encoding='utf-8'))
    assert receipt['config_sha256'] == render_review.digest(CONFIG), 'Movie needs another render for the current JSON.'
    assert receipt['sha256'] == render_review.digest(movie), 'Rendered movie checksum changed.'
    data = probe(movie)
    video = next(x for x in data['streams'] if x['codec_type'] == 'video')
    audio = next(x for x in data['streams'] if x['codec_type'] == 'audio')
    assert (video['width'], video['height']) == (1920, 1080)
    assert video['codec_name'] == 'h264' and audio['codec_name'] == 'aac'
    assert audio['sample_rate'] == '48000' and audio['channels'] == 2
    timeline = list(csv.DictReader(CONFIG.with_name('sequence-timeline.csv').open(encoding='utf-8-sig')))
    assert [x['id'] for x in timeline] == [x['id'] for x in entries]
    assert len(entries) == len({x['id'] for x in entries})
    assert float(timeline[0]['start_seconds']) == settings['opening']['seconds'] == 2
    total = float(timeline[-1]['end_seconds']) + settings['credits']['seconds']
    assert abs(float(data['format']['duration']) - total) < 0.15
    assert int(video['nb_frames']) == round(total * settings['settings']['fps'])
    chapters = subprocess.run(['ffprobe', '-v', 'error', '-show_chapters', '-of', 'json', str(movie)],
                              capture_output=True, text=True, check=True)
    assert len(json.loads(chapters.stdout)['chapters']) == len(entries) + 2
    # The first AAC-segment assembly had overlapping DTS at joins. PCM intermediates
    # must keep every audio packet ordered with no gaps beyond sample precision.
    intermediate = ROOT / 'production/local-state/review-sequence/assembled.mov'
    packet_data = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                                 '-show_entries', 'packet=pts_time,duration_time', '-of', 'json',
                                 str(intermediate)], capture_output=True, text=True, check=True)
    packets = json.loads(packet_data.stdout)['packets']
    previous_end, maximum_gap, minimum_gap = None, 0, 0
    for packet in packets:
        start = float(packet['pts_time'])
        if previous_end is not None:
            gap = start - previous_end
            maximum_gap, minimum_gap = max(maximum_gap, gap), min(minimum_gap, gap)
            assert abs(gap) < 0.00003, (start, gap)
        previous_end = start + float(packet['duration_time'])
    result = dict(status='Passed', clips=len(entries), duration_seconds=float(data['format']['duration']),
                  dimensions='1920x1080', fps=settings['settings']['fps'],
                  exact_video_frame_count=int(video['nb_frames']), chapters=len(entries)+2,
                  sequence_matches_json=True, audio='AAC stereo 48000 Hz',
                  windows_progress_reader_regression='Passed',
                  audio_join_max_gap_seconds=maximum_gap, audio_join_min_gap_seconds=minimum_gap,
                  audio_settings=settings['audio'])
    result.update(render_matches_current_json=True, movie_checksum_matches=True)
    CONFIG.with_name('validation.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

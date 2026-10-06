import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'


def chunks(text, limit=420):
    result = []
    for paragraph in re.split(r'\n\s*\n', text):
        buffer = ''
        for sentence in re.split(r'(?<=[.!?])\s+', ' '.join(paragraph.split())):
            # Split an unusually long sentence at word boundaries, without dropping words.
            for word in sentence.split():
                if buffer and len(buffer) + len(word) + 1 > limit:
                    result.append(buffer); buffer = ''
                buffer = (buffer + ' ' + word).strip()
            if buffer and len(buffer) >= limit * .65:
                result.append(buffer); buffer = ''
        if buffer:
            result.append(buffer)
    if ' '.join(' '.join(result).split()) != ' '.join(text.split()):
        raise ValueError('Text chunk coverage failed.')
    return result


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stderr[-2000:])
    return result


def main():
    import numpy as np
    import soundfile as sf
    import torch
    from kokoro import KPipeline

    request = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    job = Path(request['job_dir']); stem = Path(request['output_stem'])
    result_path = job / 'result.json'
    if result_path.exists():
        result = json.loads(result_path.read_text())
        if all(Path(result[k]).is_file() and Path(result[k]).stat().st_size == result[k + '_bytes'] for k in ('wav', 'mp3')):
            print(json.dumps({'progress': 1, 'total': 1, 'stage': 'Reused completed output'}), flush=True); return
    text_chunks = chunks(request['text'])
    if not text_chunks:
        raise ValueError('No text to speak.')
    total = len(text_chunks) + 3
    save(job / 'plan.json', {'input_sha256': request['input_sha256'], 'coverage_match': True, 'chunks': text_chunks, 'voice': request['voice'], 'speed': request['speed'], 'model_revision': request['model_revision']})
    torch.set_num_threads(4); torch.manual_seed(421)
    pipeline = None
    checkpoints = []; reused = 0; started = time.time()
    for i, text in enumerate(text_chunks):
        wav = job / f'{i:06d}.wav'; metadata = wav.with_suffix('.json')
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if wav.exists() and metadata.exists() and json.loads(metadata.read_text()).get('text_sha256') == digest:
            reused += 1
        else:
            if pipeline is None:
                pipeline = KPipeline(lang_code='b' if request['voice'].startswith('b') else 'a', repo_id='hexgrad/Kokoro-82M', device='cuda')
            generated = []; graphemes = []
            for output in pipeline(text, voice=request['voice'], speed=request['speed'], split_pattern=None):
                if len(output.phonemes) > 510:
                    raise ValueError('A text unit exceeded the model phoneme limit; split the unusually long word or sentence.')
                generated.append(output.audio.numpy().copy()); graphemes.append(output.graphemes)
            if re.findall(r'\w+', ' '.join(graphemes).lower()) != re.findall(r'\w+', text.lower()):
                raise ValueError(f'Engine text coverage failed in chunk {i + 1}.')
            audio = np.concatenate(generated)
            nz = np.flatnonzero(abs(audio) > .001)
            if len(nz):
                audio = audio[max(0, nz[0]-1920):min(len(audio), nz[-1]+2880)]
            if not len(audio) or not np.isfinite(audio).all():
                raise ValueError(f'Invalid audio in chunk {i + 1}.')
            temporary = wav.with_suffix('.partial.wav')
            sf.write(temporary, audio, 24000, subtype='PCM_16')
            temporary.replace(wav)
            save(metadata, {'text_sha256': digest, 'duration': len(audio)/24000, 'coverage_match': True})
        checkpoints.append(wav)
        print(json.dumps({'progress': i+1, 'total': total, 'stage': 'Synthesis'}), flush=True)
    # FFmpeg streams chunk files to disk; the book waveform is never held in RAM.
    pause = job / 'pause.wav'; sf.write(pause, np.zeros(6000, dtype=np.float32), 24000)
    listing = job / 'concat.txt'
    listing.write_text('\n'.join("file '" + str(p).replace('\\', '/').replace("'", "'\\''") + "'" for wav in checkpoints for p in (wav, pause)), encoding='utf-8')
    inputs = ['ffmpeg', '-hide_banner', '-f', 'concat', '-safe', '0', '-i', str(listing)]
    scan = run(inputs + ['-af', 'loudnorm=I=-19:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'])
    stats = json.loads(re.findall(r'\{[^{}]+\}', scan.stderr)[-1])
    print(json.dumps({'progress': len(text_chunks)+1, 'total': total, 'stage': 'Loudness measured'}), flush=True)
    filt = 'loudnorm=I=-19:TP=-2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true'.format(**stats)
    wav = Path(str(stem)+'.wav'); mp3 = Path(str(stem)+'.mp3')
    wave_tmp = Path(str(stem)+'.partial.wav'); mp3_tmp = Path(str(stem)+'.partial.mp3')
    run(inputs + ['-v', 'error', '-y', '-af', filt, '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', '-rf64', 'auto', str(wave_tmp)])
    wave_tmp.replace(wav)
    print(json.dumps({'progress': len(text_chunks)+2, 'total': total, 'stage': 'WAV saved'}), flush=True)
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav), '-c:a', 'libmp3lame', '-b:a', '96k', str(mp3_tmp)])
    mp3_tmp.replace(mp3)
    result = {'wav': str(wav), 'mp3': str(mp3), 'wav_bytes': wav.stat().st_size, 'mp3_bytes': mp3.stat().st_size, 'duration': sf.info(wav).duration, 'chunks': len(checkpoints), 'reused_chunks': reused, 'elapsed_seconds': time.time()-started, 'voice': request['voice'], 'speed': request['speed'], 'input_sha256': request['input_sha256'], 'coverage_match': True}
    save(result_path, result)
    print(json.dumps({'progress': total, 'total': total, 'stage': 'Complete'}), flush=True)


if __name__ == '__main__':
    main()

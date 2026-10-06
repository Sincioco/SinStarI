import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import subprocess
import threading

import folder_paths
import comfy.model_management
from comfy.utils import ProgressBar

PYTHON = Path(os.environ.get('SIN_TTS_PYTHON', ''))
VOICES = ['am_michael', 'am_fenrir', 'bm_george', 'bm_lewis', 'af_heart']
VERSION = '1.0.0-portable'


class SinAIVoicesTextToSpeech:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'source': (['Text', 'File'], {'default': 'Text'}),
            'voice': (VOICES, {'default': 'am_michael'}),
            'speed': ('FLOAT', {'default': 0.97, 'min': 0.5, 'max': 2.0, 'step': 0.01}),
            'output_name': ('STRING', {'default': 'Sin Narration'}),
            'resume': ('BOOLEAN', {'default': True}),
        }, 'optional': {
            'text': ('STRING', {'multiline': True, 'default': 'Welcome. This is Michael, reading with a calm and measured voice.'}),
            'file_path': ('STRING', {'default': '', 'tooltip': 'Absolute path to a local UTF-8 text file. Used only when Source is File.'}),
        }}

    RETURN_TYPES = ('STRING', 'STRING')
    RETURN_NAMES = ('wav_path', 'mp3_path')
    FUNCTION = 'speak'
    CATEGORY = 'Sin/AI Voices'
    OUTPUT_NODE = True
    DESCRIPTION = 'Local Kokoro voices. Text or UTF-8 file; resumable chunks, WAV and MP3. Michael is the default.'

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Recheck disk checkpoints even after a successful run or external file edit.
        return float('nan')

    @classmethod
    def VALIDATE_INPUTS(cls, source, voice, speed, text='', file_path='', **kwargs):
        if source not in ('Text', 'File') or voice not in VOICES:
            return 'Select a supported source and voice.'
        if not math.isfinite(speed) or speed <= 0:
            return 'Speed must be a positive number.'
        if source == 'Text' and not text.strip():
            return 'Enter text, or select File and supply a UTF-8 text file.'
        if source == 'File' and not Path(file_path.strip().strip('"')).is_file():
            return 'The text file was not found. Supply an existing local file path.'
        return True

    def speak(self, source, voice, speed, output_name, resume, text='', file_path=''):
        valid = self.VALIDATE_INPUTS(source, voice, speed, text, file_path)
        if valid is not True:
            raise ValueError(valid)
        content = Path(file_path.strip().strip('"')).read_text(encoding='utf-8-sig') if source == 'File' else text
        if not content.strip():
            raise ValueError('The selected text file is empty.')
        if not PYTHON.is_file():
            raise FileNotFoundError(f'Kokoro Python was not found: {PYTHON}')
        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', output_name).strip(' .') or 'Sin Narration'
        if re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])', name):
            name = 'Sin ' + name
        name = name[:100]
        settings = {'voice': voice, 'speed': speed, 'version': VERSION, 'model_revision': 'f3ff3571791e39611d31c381e3a41a3af07b4987'}
        key = hashlib.sha256((json.dumps(settings, sort_keys=True) + '\n' + content).encode('utf-8')).hexdigest()[:16]
        if not resume:
            key += '-' + os.urandom(4).hex()
        output_root = Path(folder_paths.get_output_directory()).resolve()
        root = (output_root / 'Sin-AI-Voices-TTS').resolve()
        if not root.is_relative_to(output_root):
            raise ValueError('The speech output directory must remain inside ComfyUI output.')
        job = (root / '.checkpoints' / (name + '-' + key)).resolve()
        if not job.is_relative_to(root):
            raise ValueError('Invalid checkpoint location.')
        job.mkdir(parents=True, exist_ok=True)
        request = {**settings, 'text': content, 'job_dir': str(job), 'output_stem': str(root / (name + '-' + key)), 'input_sha256': hashlib.sha256(content.encode('utf-8')).hexdigest()}
        request_path = job / 'request.json'
        request_path.write_text(json.dumps(request, ensure_ascii=False), encoding='utf-8')
        messages = queue.Queue()
        progress = ProgressBar(1)
        proc = subprocess.Popen([str(PYTHON), '-u', str(Path(__file__).with_name('runner.py')), str(request_path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        def read_output():
            for line in proc.stdout:
                messages.put(line)
        reader = threading.Thread(target=read_output, daemon=True)
        reader.start()
        tail = []
        try:
            while proc.poll() is None or reader.is_alive() or not messages.empty():
                comfy.model_management.throw_exception_if_processing_interrupted()
                try:
                    line = messages.get(timeout=0.15)
                except queue.Empty:
                    continue
                if line.startswith('{"progress"'):
                    event = json.loads(line)
                    progress.update_absolute(event['progress'], event['total'])
                else:
                    tail.append(line.rstrip()); tail = tail[-20:]
            if proc.returncode:
                raise RuntimeError('Kokoro rendering failed. ' + '\n'.join(tail)[-2500:])
        finally:
            if proc.poll() is None:
                subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                proc.wait(timeout=15)
            reader.join(timeout=2)
            proc.stdout.close()
        result = json.loads((job / 'result.json').read_text(encoding='utf-8'))
        wav, mp3 = Path(result['wav']), Path(result['mp3'])
        for path in (wav, mp3):
            if not path.resolve().is_relative_to(output_root) or not path.is_file():
                raise RuntimeError('The speech output is missing or outside the output folder.')
        relative = mp3.relative_to(output_root)
        return {'ui': {'audio': [{'filename': relative.name, 'subfolder': relative.parent.as_posix(), 'type': 'output'}]}, 'result': (str(wav), str(mp3))}


NODE_CLASS_MAPPINGS = {'SinAIVoicesTextToSpeech': SinAIVoicesTextToSpeech}
NODE_DISPLAY_NAME_MAPPINGS = {'SinAIVoicesTextToSpeech': 'Sin - AI Voices - Text to Speech'}

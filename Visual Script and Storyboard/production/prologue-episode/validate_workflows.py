"""Regression check: every saved workflow image must be selectable in ComfyUI."""
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
LIBRARY = Path(r'D:\Sin - AI Prompt\work\comfy_photo_video_user\default\workflows\Sin Star I Prologue Episode')


def main():
    with urllib.request.urlopen('http://127.0.0.1:8191/object_info/LoadImage') as response:
        info = json.load(response)
    choices = info['LoadImage']['input']['required']['image'][0]
    paths = list(HERE.rglob('*-ui.json'))
    assert len(paths) == 23
    for path in paths:
        ui = json.loads(path.read_text(encoding='utf-8'))
        image = next(n for n in ui['nodes'] if n['id'] == 1)
        name = image['widgets_values'][0]
        assert name in choices, (path.name, name)
        assert image['widgets_values_named']['image'] == name
        api = json.loads(path.with_name(path.name.replace('-ui.json', '-api.json')).read_text(encoding='utf-8'))
        assert api['1']['inputs']['image'] == name
        shot = next(n for n in ui['nodes'] if n['id'] == 101)
        width, height = shot['widgets_values'][3:5]
        assert width * 9 == height * 16
        save = next(n for n in ui['nodes'] if n['id'] == 901)
        published = LIBRARY / (Path(save['widgets_values'][0]).name + '.json')
        assert json.loads(published.read_text(encoding='utf-8')) == ui
    print(f'Passed: {len(paths)} selectable reference images, matching saved/API workflows and 16:9 dimensions.')


if __name__ == '__main__':
    main()

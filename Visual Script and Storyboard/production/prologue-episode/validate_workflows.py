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
    assert paths, 'No saved workflows found.'
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
        assert width % 64 == height % 64 == 0
        latent = api['101:437']['inputs']
        assert (latent['width'] * 2, latent['height'] * 2) == (width, height)
        crop = api.get('101:902')
        if crop:
            c = crop['inputs']
            assert c['width'] * 9 == c['height'] * 16
            assert c['width'] + 2 * c['x'] == width
            assert c['height'] + 2 * c['y'] == height
            assert api['101:451']['inputs']['images'] == ['101:902', 0]
            group = next(g for g in ui['definitions']['subgraphs']
                         if any(n['id'] == 902 for n in g['nodes']))
            crop_ui = next(n for n in group['nodes'] if n['id'] == 902)
            assert crop_ui['widgets_values'] == [c[k] for k in ('width', 'height', 'x', 'y')]
            outgoing = crop_ui['outputs'][0]['links'][0]
            assert next(n for n in group['nodes'] if n['id'] == 451)['inputs'][0]['link'] == outgoing
        else:
            assert width * 9 == height * 16
        save = next(n for n in ui['nodes'] if n['id'] == 901)
        published = LIBRARY / (Path(save['widgets_values'][0]).name + '.json')
        assert json.loads(published.read_text(encoding='utf-8')) == ui
    print(f'Passed: {len(paths)} selectable reference images, matching saved/API workflows and 16:9 dimensions.')


if __name__ == '__main__':
    main()

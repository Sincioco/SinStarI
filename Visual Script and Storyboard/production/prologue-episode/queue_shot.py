"""Queue one episode shot using the existing LTX 2.5 production templates."""
import argparse
import json
from pathlib import Path
import shutil
import sys

PRODUCTION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCTION))
from queue_hover import ROOT, INPUT, build_graph, request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('shot', type=Path)
    args = parser.parse_args()
    item = json.loads(args.shot.read_text(encoding='utf-8'))
    receipt = args.shot.with_name(item['id'] + '-receipt.json')
    INPUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / item['image'], INPUT / (item['id'] + '.png'))
    templates = PRODUCTION / 'templates'
    api_template = json.loads((templates / 'Room-for-One-API.json').read_text(encoding='utf-8'))
    ui_template = json.loads((templates / 'Sin Star I - Room for One - LTX 2.5 - 24 Seconds.json').read_text(encoding='utf-8'))
    graph, ui, prompt = build_graph(item, 0, api_template, ui_template)
    # This ComfyUI image picker lists only the input directory's top level.
    # Subfolder paths render through the API but reopen as missing UI inputs.
    image_name = 'SinStarI_Prologue_' + item['id'] + '.png'
    shutil.copy2(ROOT / item['image'], INPUT.parent / image_name)
    graph['1']['inputs']['image'] = image_name
    load = next(node for node in ui['nodes'] if node['id'] == 1)
    load['widgets_values'][0] = image_name
    load['widgets_values_named']['image'] = image_name
    name = item.get('output_name', item['id'])
    prefix = 'SinStarI_PrologueEpisode/' + name
    graph['901']['inputs']['filename_prefix'] = prefix
    save = next(node for node in ui['nodes'] if node['id'] == 901)
    save['widgets_values'][0] = prefix
    save.setdefault('widgets_values_named', {})['filename_prefix'] = prefix
    ui['extra']['ds'] = {'scale': 0.75, 'offset': [80, 200]}
    for suffix, data in [('-api.json', graph), ('-ui.json', ui)]:
        args.shot.with_name(item['id'] + suffix).write_text(json.dumps(data, indent=2), encoding='utf-8')
    library = Path(r'D:\Sin - AI Prompt\work\comfy_photo_video_user\default\workflows\Sin Star I Prologue Episode')
    library.mkdir(parents=True, exist_ok=True)
    (library / (name + '.json')).write_text(json.dumps(ui, indent=2), encoding='utf-8')
    if receipt.exists():
        print(receipt.read_text(encoding='utf-8'))
        return
    result = request('/prompt', {'prompt': graph, 'extra_data': {
        'extra_pnginfo': {'workflow': ui}, 'workflow_name': item['caption']}})
    if result.get('node_errors'):
        raise RuntimeError(result)
    receipt.write_text(json.dumps(dict(result, id=item['id'], prompt=prompt), indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

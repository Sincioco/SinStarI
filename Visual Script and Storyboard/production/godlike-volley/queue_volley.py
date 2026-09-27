"""Queue the moving Godlike take with the following shot as the final-frame guide."""
import copy
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from queue_hover import build_graph, request


def main():
    receipt = HERE / 'volley-receipt.json'
    if receipt.exists():
        print(receipt.read_text())
        return
    spec = json.loads((HERE / 'volley.json').read_text(encoding='utf-8'))
    inputs = Path(r'D:\AI\Mira3D\ComfyUI\input')
    for source, name in [('dynamic-start.png', 'SinStarI_Godlike_Volley_Start.png'),
                         ('references/next-first-frame.png', 'SinStarI_Godlike_Volley_End.png')]:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(HERE / source),
                        '-vf', 'scale=1280:720:flags=lanczos,pad=1280:768:0:24',
                        '-frames:v', '1', str(inputs / name)], check=True)
    templates = HERE.parent / 'templates'
    graph, ui, _ = build_graph(spec, 0,
        json.loads((templates / 'Room-for-One-API.json').read_text()),
        json.loads((templates / 'Sin Star I - Room for One - LTX 2.5 - 24 Seconds.json').read_text()))
    graph['1']['inputs']['image'] = 'SinStarI_Godlike_Volley_Start.png'
    load = next(n for n in ui['nodes'] if n['id'] == 1)
    load['widgets_values'][0] = graph['1']['inputs']['image']
    load['widgets_values_named']['image'] = graph['1']['inputs']['image']
    graph['901']['inputs']['filename_prefix'] = 'SinStarI_GodlikeVolley/Moving_Godlike_720p'
    save = next(n for n in ui['nodes'] if n['id'] == 901)
    save['widgets_values'][0] = graph['901']['inputs']['filename_prefix']
    guide = json.loads((HERE.parent / 'workflows/new-c00-s01-duel-godlike-continuity-api.json').read_text())
    for key in ['2', '910', '911', '912', '913']:
        graph[key] = copy.deepcopy(guide[key])
    graph['2']['inputs']['image'] = 'SinStarI_Godlike_Volley_End.png'
    graph['2']['_meta']['title'] = 'Who Are You — Exact Opening Pose'
    rewires = {'101:427': ['positive', 'negative'], '101:432': ['video_latent'],
               '101:438': ['samples'], '101:443': ['video_latent'],
               '101:445': ['positive', 'negative'], '101:449': ['samples']}
    for key, names in rewires.items():
        for name in names:
            graph[key]['inputs'][name] = guide[key]['inputs'][name]

    # Keep the editable ComfyUI workflow equivalent to the submitted API graph.
    group = next(g for g in ui['definitions']['subgraphs'] if any(n['id'] == 449 for n in g['nodes']))
    info = request('/object_info')
    mapping = {'2': 909, '910': 910, '911': 911, '912': 912, '913': 913}
    for key, node_id in mapping.items():
        api = graph[key]
        schema = info[api['class_type']]
        ports, widgets, named = [], [], {}
        for name, value in api['inputs'].items():
            field = schema['input'].get('required', {}).get(name) or schema['input'].get('optional', {}).get(name)
            kind = field[0]
            port = dict(name=name, type='COMBO' if isinstance(kind, list) else kind, link=None)
            if not isinstance(value, list):
                port['widget'] = dict(name=name)
                widgets.append(value)
                named[name] = value
            ports.append(port)
        if api['class_type'] == 'LoadImage':
            widgets.append('image')
        group['nodes'].append(dict(id=node_id, type=api['class_type'], pos=[1300 + (node_id - 909) * 650, 8000],
            size=[320, 250], flags={}, order=50 + node_id - 909, mode=0, inputs=ports,
            outputs=[dict(name=name, type=kind, links=[]) for name, kind in zip(schema['output_name'], schema['output'])],
            properties={'Node name for S&R': api['class_type'], 'cnr_id': 'comfy-core'},
            widgets_values=widgets, widgets_values_named=named, title=api.get('_meta', {}).get('title', api['class_type'])))
    nodes = {n['id']: n for n in group['nodes']}

    def connect(key, name, reference):
        target = nodes[mapping.get(key, int(key.split(':')[-1]))]
        slot = next(i for i, p in enumerate(target['inputs']) if p['name'] == name)
        port = target['inputs'][slot]
        old = port.get('link')
        if old:
            previous = next(link for link in group['links'] if link['id'] == old)
            origin = nodes.get(previous['origin_id'])
            if origin:
                origin['outputs'][previous['origin_slot']]['links'].remove(old)
            group['links'].remove(previous)
        source_key, source_slot = reference
        source_id = mapping.get(source_key, int(source_key.split(':')[-1]))
        group['state']['lastLinkId'] += 1
        link_id = group['state']['lastLinkId']
        group['links'].append(dict(id=link_id, origin_id=source_id, origin_slot=source_slot,
                                  target_id=target['id'], target_slot=slot, type=port['type']))
        port['link'] = link_id
        nodes[source_id]['outputs'][source_slot].setdefault('links', []).append(link_id)

    for key in mapping:
        for name, value in graph[key]['inputs'].items():
            if isinstance(value, list):
                connect(key, name, value)
    for key, names in rewires.items():
        for name in names:
            connect(key, name, graph[key]['inputs'][name])
    group['state']['lastNodeId'] = max(group['state']['lastNodeId'], 913)
    for suffix, data in [('api', graph), ('ui', ui)]:
        (HERE / f'volley-{suffix}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    library = Path(r'D:\Sin - AI Prompt\work\comfy_photo_video_user\default\workflows\Sin Star I Prologue Episode')
    (library / 'C00-S01 - Moving Godlike Volley - 720p.json').write_text(json.dumps(ui, ensure_ascii=False, indent=2), encoding='utf-8')
    result = request('/prompt', dict(prompt=graph, extra_data=dict(extra_pnginfo=dict(workflow=ui),
        workflow_name='Sin Star I - C00-S01 - Moving Godlike Volley - 720p')))
    if result.get('node_errors'):
        raise ValueError(result)
    receipt.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

"""Add reviewed episode takes as alternatives without replacing older media."""
import json
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
from build_draft3 import picture
from youtube_catalog import prepare
from review_catalog import sync_review_catalog


def export_settings(identifier, shot):
    paths = [HERE / 'shots' / f'{identifier}.json', HERE / f'{identifier}.json',
             HERE / 'shots' / f'{identifier.removesuffix("-bridge")}.json']
    spec = next((json.loads(path.read_text(encoding='utf-8')) for path in paths if path.is_file()), {})
    # The original memory take predates shot specs and was exported at 1024 x 576.
    return dict(output_size=spec.get('render_size', [1024, 576]),
                render_seconds=spec.get('render_seconds', shot['seconds']))


def replace_picture(source, item):
    marker = f'<div class="animated-picture" data-media-id="{item["id"]}"'
    start = source.find(marker)
    if start < 0:
        raise ValueError('Illustration not found: ' + item['id'])
    depth = 0
    for match in re.finditer(r'</?div\b[^>]*>', source[start:]):
        depth += -1 if match[0].startswith('</') else 1
        if depth == 0:
            end = start + match.end()
            break
    original = source[start:end]
    link = re.search(r'<a\b[^>]*>.*?</a>', original, re.S)[0]
    link = re.sub(r'<video\b[^>]*>.*?</video>', '', link, flags=re.S)
    return source[:start] + picture(link, item) + source[end:]


def main():
    episode = json.loads((HERE / 'episode.json').read_text(encoding='utf-8'))
    shots = {shot['id']: shot for shot in episode['shots']}
    approved = json.loads((HERE / 'accepted.json').read_text(encoding='utf-8'))
    path = HERE.parent / 'hover-media.json'
    items = json.loads(path.read_text(encoding='utf-8'))
    parents = {item['id']: item for item in items}
    changed = set()
    for identifier, acceptance in approved.items():
        shot = shots[acceptance['shot']]
        parent = parents[shot['parent']]
        title = acceptance.get('title', acceptance['shot'].replace('-', ' ').title())
        scale = acceptance.get('scale', 'Close' if shot['parent'] in ('panel-01-1', 'new-c00-s02-contract') else 'Wide')
        variants = parent.setdefault('variants', [])
        variant = next((v for v in variants if v['id'] == identifier), None)
        if variant is None:
            variant = dict(id=identifier)
            variants.append(variant)
        number = variants.index(variant) + 2
        video = f'asset/videos/hover/{parent["scene"].upper()}_Clip{number} - {scale} - {title}.mp4'
        target = ROOT / video
        source = ROOT / acceptance['file']
        if not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
            shutil.copy2(source, target)
        variant.update(video=video, source=acceptance['file'], status='reuse',
                       caption='Prologue episode — ' + title,
                       youtube_title=f'Sin Star I - Prologue - Room for One - {parent["scene"].upper()}_Clip{number} - {scale} / {title}',
                       provenance='LTX 2.5 episode take; ' + acceptance['review'],
                       dialogue=shot['dialogue'])
        variant.update(export_settings(identifier, shot))
        if acceptance.get('episode_use') is False:
            variant['caption'] += ' — Retained alternate; see review note'
            variant['review_note'] = acceptance['review']
        elif acceptance.get('dream_bridge'):
            variant['caption'] += ' — Corrected dream sound'
        changed.add(parent['id'])
        if acceptance['shot'] == 'memory' or (acceptance['shot'] == 'wake' and acceptance.get('episode_use', True)):
            parent['default_clip'] = identifier
        acceptance['video'] = video
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (HERE / 'accepted.json').write_text(json.dumps(approved, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for page in ['index.html', 'Sin-Star-I-Game-Script-v0.2.html']:
        path = ROOT / page
        source = path.read_text(encoding='utf-8')
        for identifier in sorted(changed):
            source = replace_picture(source, parents[identifier])
        path.write_text(source, encoding='utf-8')
    prepare()
    sync_review_catalog()
    print(f'{len(approved)} episode alternatives available in both views.')


if __name__ == '__main__':
    main()

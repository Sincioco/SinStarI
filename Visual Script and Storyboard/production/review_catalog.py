"""Add published takes to live/movie review without replacing editorial choices."""
import json
from pathlib import Path
import tempfile

from media_catalog import clips_for

ROOT = Path(__file__).resolve().parents[1]


def merge_catalog(config, items, root=ROOT):
    entries = config['clips']
    added = []
    for parent in items:
        family = clips_for(parent)
        anchor = next((entry for entry in entries if entry['id'] == parent['id']), None)
        for clip in family:
            existing = next((entry for entry in entries
                             if entry['id'] == clip['id'] or entry['file'] == clip['video']), None)
            if existing:
                anchor = existing
                continue
            if not (root / clip['video']).is_file():
                continue  # Queued/unfinished renders do not become broken picker entries.
            scene = clip['scene'].upper()
            peer = anchor or next((entry for entry in reversed(entries) if entry['scene'] == scene), None)
            title = Path(clip['video']).stem.split(' - ', 1)[-1].replace(' - ', ' / ')
            variation = Path(clip['video']).stem.split(' - ', 1)[0].partition('_Clip')[2]
            entry = dict(id=clip['id'], enabled=True, file=clip['video'],
                         chapter=clip.get('chapter_title', peer['chapter'] if peer else ''),
                         scene=scene, scene_title=peer['scene_title'] if peer else clip['caption'],
                         take=(f'Clip {variation} / ' if variation else '') + title,
                         context=clip['caption'],
                         muted=False)
            entries.insert(entries.index(peer) + 1 if peer else len(entries), entry)
            anchor = entry
            added.append(clip['id'])
    return added


def sync_review_catalog():
    path = ROOT / 'production/review-sequence/sequence.json'
    original = path.read_bytes()
    config = json.loads(original.decode('utf-8-sig'))
    items = json.loads((ROOT / 'production/hover-media.json').read_text(encoding='utf-8'))
    added = merge_catalog(config, items)
    if added:
        # Preserve live saves: do not replace a config that changed during this merge.
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write((json.dumps(config, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        try:
            if path.read_bytes() != original:
                raise RuntimeError('Review settings changed; run catalog sync again.')
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    print(f'Review catalog: added {len(added)} clips; {len(config["clips"])} available; saved choices preserved.')
    return added


if __name__ == '__main__':
    sync_review_catalog()

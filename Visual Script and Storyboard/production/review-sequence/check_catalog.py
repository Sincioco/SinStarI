"""Regression: published alternatives reach review and excluded takes skip rendering."""
import copy
import csv
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media_catalog import all_clips
from review_catalog import ROOT, merge_catalog
import render_review


def main():
    config = json.loads((ROOT / 'production/review-sequence/sequence.json').read_text(encoding='utf-8'))
    catalog = json.loads((ROOT / 'production/hover-media.json').read_text(encoding='utf-8'))
    published = [clip for clip in all_clips(catalog) if (ROOT / clip['video']).is_file()]
    assert {clip['video'] for clip in published} <= {entry['file'] for entry in config['clips']}
    original = copy.deepcopy(config)
    assert merge_catalog(config, catalog) == [] and config == original
    # Recreate the actual stale-sequence bug without touching live settings.
    take = next(clip for clip in published if clip['id'].startswith('episode-'))
    config['clips'] = [entry for entry in config['clips'] if entry['id'] != take['id']]
    config['clips'][0].update(enabled=False, muted=True, duration_seconds=0.5)
    prior = copy.deepcopy(config['clips'])
    assert merge_catalog(config, catalog) == [take['id']]
    assert [entry for entry in config['clips'] if entry['id'] != take['id']] == prior
    assert merge_catalog(config, catalog) == []

    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        # These two newly listed takes exposed overlong production notes in movie panels.
        panels = copy.deepcopy(original)
        for layout in ('overlay', 'side-by-side'):
            panels['settings']['layout'] = layout
            for entry in panels['clips']:
                if entry['id'] in ('episode-wake-take5', 'episode-wake-take7'):
                    render_review.overlay(entry, 1, len(panels['clips']), temporary / 'panel.png', panels)
        settings = copy.deepcopy(original)
        included = copy.deepcopy(settings['clips'][0])
        included.update(enabled=True, duration_seconds=0.5)
        excluded = dict(included, id='excluded-missing-file', enabled=False, file='does-not-exist.mp4')
        settings['clips'] = [excluded, included]
        path = temporary / 'inclusion.json'
        path.write_text(json.dumps(settings), encoding='utf-8')
        old_cache = render_review.CACHE
        try:
            render_review.CACHE = temporary
            render_review.render(path, prepare_only=True)
            rows = list(csv.DictReader(path.with_name('inclusion-timeline.csv').open(encoding='utf-8-sig')))
            assert [row['id'] for row in rows] == [included['id']]
            settings['clips'][0].update(enabled=True, file=included['file'])
            path.write_text(json.dumps(settings), encoding='utf-8')
            render_review.render(path, prepare_only=True)
            rows = list(csv.DictReader(path.with_name('inclusion-timeline.csv').open(encoding='utf-8-sig')))
            assert [row['id'] for row in rows] == [excluded['id'], included['id']]
        finally:
            render_review.CACHE = old_cache
    print(f'Passed: all {len(published)} published clips present; sync preserves choices/order and is idempotent; renderer excludes and re-includes clips.')


if __name__ == '__main__':
    main()

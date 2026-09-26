"""Turn the approved episode breakdown into separate, reproducible LTX shots."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    episode = json.loads((HERE / 'episode.json').read_text(encoding='utf-8'))
    folder = HERE / 'shots'
    folder.mkdir(exist_ok=True)
    for index, shot in enumerate(episode['shots']):
        if 'reuse' in shot or shot['id'] == 'memory':
            continue
        identifier = 'episode-' + shot['id'] + '-take1'
        lines = shot['dialogue']
        speech = ' '.join(f'{speaker} says exactly, "{line}".' for speaker, line in lines)
        audio = (f'The audible English dialogue in this shot, in this exact order, is: {speech} '
                 'Every complete sentence is spoken clearly by its assigned character, naturally timed, '
                 'one speaker at a time. Mouth movements follow the audible speech. Finish every line '
                 'before the clip ends and remain silent afterward. No other words are spoken. '
                 if lines else 'No intelligible speech or words. Nobody narrates or sings. ')
        prompt = (f'One continuous {shot["seconds"]}-second cinematic painted anime film shot, '
                  'landscape 16:9, based on the supplied first-frame illustration. '
                  'Preserve these exact character faces, hairstyles, clothing, armor, props and setting '
                  'throughout the motion. Natural detailed anatomy, expressive restrained acting, '
                  'smooth physically coherent motion, rich cinematic light and fine painted textures. '
                  + shot['action'] + ' ' + audio +
                  'Clear foreground audio and quiet environmental sound, no background music. '
                  'The picture remains completely clean: absolutely no written words, no subtitles, '
                  'no captions, no lettering, no logos, no dialogue bubbles or screen graphics. '
                  'Only move lips when that character is the speaker. No cut, no sudden identity change.')
        item = dict(id=identifier, image=shot['image'], caption='Prologue Episode | ' + shot['id'],
                    art=shot['action'], render_size=[1280, 720], render_seconds=shot['seconds'],
                    seed=202609270200 + index, motion_prompt=prompt,
                    negative_prompt='subtitles, captions, text, writing, letters, logos, dialogue bubbles, '
                    'gibberish, extra dialogue, overlapping voices, narrator, singing, music, '
                    'deformed anatomy, duplicate characters, identity changes, split screen, camera cuts',
                    dialogue=[dict(speaker=speaker, text=line) for speaker, line in lines], parent=shot['parent'])
        path = folder / (identifier + '.json')
        if not path.exists():
            path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
        if not (ROOT / item['image']).exists():
            print('Waiting for image: ' + item['image'], flush=True)
            continue
        if not path.with_name(identifier + '-receipt.json').exists():
            subprocess.run([sys.executable, str(HERE / 'queue_shot.py'), str(path)], check=True)


if __name__ == '__main__':
    main()

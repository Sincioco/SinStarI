"""Add five requested World Hurled treatments; keep both accepted earlier takes."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
catalog = ROOT / 'production/hover-media.json'

COMMON = (
    'A continuous TEN-SECOND epic cinematic fantasy battle beginning from the supplied image. '
    'Enormous four-armed cosmic god Aevos towers over the same small party on the causeway. '
    'The ONE large blue-brown planet rests above his upper palm on screen left. '
    'Mira is the brown-haired woman holding the ring staff near center-left. '
    'All heroes are seen from behind facing the god. Preserve their distinct equipment, '
    'positions and normal anatomy: Arin has cyan sword and kite shield, Mira has ring staff, '
    'Orin carries the rectangular tower shield, Zara is one red mechanical robot, '
    'Milo is ONE four-legged golden-white dog. Kael remains at the far right. '
    'Mira has one head attached naturally to her neck, two arms, two legs; her head, spine '
    'and hips move together in the same direction. Nobody turns their head toward the camera. '
    '0-2 seconds: Aevos winds up with his planet-bearing arm, then contemptuously HURLS '
    'and RELEASES the entire round planet toward the party. His raised hand becomes empty. '
    '2-4 seconds: the planet crosses the space from upper left to the blue shield, '
    'growing nearer with clearly visible continents and swirling clouds. Mira braces '
    'and pours bright turquoise power from her palm into the barrier. '
    '4-6 seconds: the planet collides with Mira\'s shield. The dome absorbs most of '
    'the impact and stays intact for a moment. The PLANET BREAKS APART into enormous '
    'rock plates and glowing debris against the outside of the dome. The intact globe '
    'is now completely gone. Debris streams around the heroes. '
    '6-8 seconds: after that brief victory the strained shield develops spreading '
    'fractures, then SHATTERS into blue luminous shards. A second blast pushes every '
    'hero backward along the causeway; their feet slide, knees buckle, cloaks whip. '
    'Mira\'s head and torso recoil together, without neck twisting or body distortion. '
    '8-10 seconds: Arin and Orin catch themselves low against the stones; Mira lands '
    'on a knee with her staff planted; Zara shields the crouching dog. They are alive '
    'but barely holding on. No shield remains, no whole planet remains, only debris '
    'and dust; Aevos stands untouched, overwhelmingly powerful. '
    'Preserve readable spatial cause and effect and the detailed painted cosmic style. '
    'No gore, additional people, duplicated limbs, face changes, dialogue, subtitles, '
    'lettering or logos. Sound: immense low rumble, accelerating air, crushing planetary '
    'impact, rocky fragmentation, a clear glasslike shield-break after the first blast, '
    'and a final rolling shockwave. No speech or music. '
)

TREATMENTS = [
    ('Locked Wide', 'Locked wide camera behind the heroes. Show the full throw, impact and '
     'backward slide clearly in the same composition. Two distinct waves of force.'),
    ('Crushing Impact', 'Very slow cinematic push toward the shield until impact, then a '
     'small physical camera jolt on each of the TWO separate blasts. Stay behind the heroes.'),
    ('Moment of Hope', 'A restrained wide camera. Emphasize one second of terrible stillness '
     'after the world crumbles against the intact shield, before blue cracks race outward '
     'and the dome explodes. Keep every silhouette easy to read.'),
    ('Godlike Scale', 'Gently pull the wide camera backward during the approach, revealing '
     'more of Aevos and the tiny party. He barely moves after the throw. The heroes skid '
     'only a short distance, retaining their bodies and identities.'),
    ('Last Stand', 'Locked composition with a very brief slow-motion emphasis at shield '
     'rupture: blue fragments, streaming cloth and a coordinated backward recoil. '
     'End on battered survivors low to the ground under the vast unhurt god.')
]

def main():
    items = json.loads(catalog.read_text(encoding='utf-8'))
    planet = next(x for x in items if x['id'] == 'new-c09-s03-planet')
    for number, (label, treatment) in enumerate(TREATMENTS, 3):
        identifier = f'new-c09-s03-planet-take{number}'
        if any(x['id'] == identifier for x in planet['variants']):
            continue
        planet['variants'].append(dict(
            id=identifier, video=f'asset/videos/hover/C09-S03_Clip{number} - Final Battle - World Hurled.mp4',
            seed=202609160936 + number * 101, render_seconds=10, status='needs_render',
            caption=f'World Hurled — {label}', shot_title='Final Battle / World Hurled',
            chapter_title=planet['chapter_title'],
            youtube_title=f'Sin Star I - Chapter 09 - Final Battle - C09-S03 - World Hurled - {number}',
            motion_prompt=COMMON + treatment))
    catalog.write_text(json.dumps(items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Five new variations prepared; previous two clips preserved.')

if __name__ == '__main__':
    main()

"""Refresh the offline shell version after HTML/CSS/JS or storyboard image edits."""
import hashlib,json
from pathlib import Path
W=Path(globals().get('WEB_ROOT',Path(__file__).resolve().parents[1]))
book=json.loads((W/'book.json').read_text(encoding='utf-8'))
registry=W/'storyboards.json'
if not registry.exists():registry.write_text('{"images": []}\n',encoding='utf-8')
images=json.loads(registry.read_text(encoding='utf-8'))['images']
files=['index.html','reader.css','app.js','cue-navigation.js','follow-narration.js','offline.js','music.js','music-cache.js','music.json','bookmarks.js','bookmark-anchors.js','book.json','manifest.webmanifest','icon.svg','storyboards.json']
for image in images:
    path=(W/image).resolve()
    if not path.is_relative_to(W.resolve()) or not path.is_file():raise ValueError('Storyboard image must exist inside web: '+image)
    files.append(path.relative_to(W.resolve()).as_posix())
template=(W/'production/sw.template.js').read_text(encoding='utf-8')
revision=hashlib.sha256(template.encode()+b''.join((W/name).read_bytes() for name in files)).hexdigest()[:16]
assets=['./']+['./'+name for name in files]
(W/'sw.js').write_text(template.replace('__AUDIO_VERSION__',book['version']).replace('__SHELL_VERSION__',revision).replace('__SHELL_ASSETS__',json.dumps(assets)),encoding='utf-8')
print(json.dumps({'shell_version':revision,'cached_shell_assets':len(assets),'registered_storyboard_images':len(images)}))

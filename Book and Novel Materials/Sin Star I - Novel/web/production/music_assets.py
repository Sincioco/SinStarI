"""Export unchanged music copies; narration files and originals are never edited."""
import hashlib,json,shutil,subprocess
from pathlib import Path

TRACKS=[('Starforge Horizon (Title Screen)','starforge-horizon'),('Starforge March (Orin)','starforge-march'),('Bloom (Arin)','bloom')]
def export_music(web,source):
    (web/'music').mkdir(exist_ok=True)
    tracks=[]
    for title,slug in TRACKS:
        original=source/(title+'.mp3');target=web/'music'/(slug+'.mp3')
        data=original.read_bytes();digest=hashlib.sha256(data).hexdigest()
        if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:shutil.copy2(original,target)
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(original)]))
        tracks.append(dict(file='music/'+target.name,title=title,bytes=len(data),sha256=digest,duration=duration))
    (web/'music.json').write_text(json.dumps({'tracks':tracks},indent=2)+'\n',encoding='utf-8')

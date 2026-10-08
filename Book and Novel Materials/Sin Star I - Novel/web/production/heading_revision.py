"""Apply a reviewed local audio-prefix manifest without altering accepted bodies."""
from pathlib import Path
import hashlib,json,html,re,shutil

def digest(data):return hashlib.sha256(data).hexdigest()
def load_revision(web,novel,override=None):
    config=web/'production/heading-revision.json'
    if not override and not config.exists():return None
    path=Path(override) if override else novel/json.loads(config.read_text(encoding='utf8'))['manifest']
    data=json.loads(path.read_text(encoding='utf8'));assert data['sections']==42
    data['_root']=path.parent
    data['_baseline']=json.loads((path.parent/'baseline-book.json').read_text(encoding='utf8'))
    assert data['_baseline']['version']==data['previous_version']
    return data

def apply_chapter(revision,web,index,chapter,section):
    if not revision:return section
    record=revision['records'][index];old=revision['_baseline']['chapters'][index+1]
    assert record['chapterId']==chapter['id'] and record['label']==chapter['label'] and record['title']==chapter['title']
    assert chapter['sha256']==old['sha256']==record['accepted_mobile_sha256']
    assert record['body_pcm_preserved_in_assembly'] and record['accepted_master_essence_reproduced']
    source=revision['_root']/record['file'];raw=source.read_bytes()
    assert digest(raw)==record['sha256'] and len(raw)==record['bytes']
    name=f'audio/{index:02d}-headings-v1.mp3';target=web/name
    if not target.exists() or digest(target.read_bytes())!=record['sha256']:shutil.copy2(source,target)
    offset=record['bodyStart'];heading_cues=[]
    for part,text,start,end in [('label',chapter['label'],'labelStart','labelEnd'),('title',chapter['title'],'titleStart','titleEnd')]:
        cue_id=chapter['id']+'-heading-'+part;plain=' '.join(re.findall(r'[\w]+',text))
        heading_cues.append({'id':cue_id,'start':record[start],'end':record[end],'text':plain,'textHash':digest(plain.encode()),'kind':'heading'})
        escaped=html.escape(text)
        if part=='label':
            old_markup='<p class="label">'+escaped+'</p>'
            new_markup='<p class="label" id="'+chapter['id']+'-label" data-narratable="true"><span data-cue-id="'+cue_id+'">'+escaped+'</span></p>'
            assert old_markup in section;section=section.replace(old_markup,new_markup,1)
        else:
            pattern=r'(<h2\b[^>]*)(>)'+re.escape(escaped)+r'(</h2>)'
            section,count=re.subn(pattern,lambda m:m[1]+' data-narratable="true">'+'<span data-cue-id="'+cue_id+'">'+escaped+'</span>'+m[3],section,count=1)
            assert count==1
    chapter.update(audio=name,bytes=record['bytes'],sha256=record['sha256'],duration=record['duration_seconds'],bodyStart=offset,
                   cues=heading_cues+[{**cue,'start':cue['start']+offset,'end':cue['end']+offset} for cue in chapter['cues']])
    return section

def revision_metadata(revision):
    if not revision:return {}
    return {'audioRevision':revision['revision']}

"""Project-specific, dependency-free ID3v2.4 tag update; no audio re-encoding.

Run from the audiobook folder: python apply_chapter_metadata.py --apply
Without --apply, create and verify staged copies only. --resume RUN_FOLDER
continues an existing run, including files previously locked by another app.
"""
import argparse,csv,hashlib,json,os,re,shutil,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path

P=Path(__file__).resolve().parent
TARGETS={'TIT2','TPE1','TALB'}
def sha(data):return hashlib.sha256(data).hexdigest()
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8');tmp.replace(path)
def decode_size(raw):
    assert len(raw)==4 and all(b<128 for b in raw),'Invalid synchsafe size'
    return sum(b<<(7*(3-i)) for i,b in enumerate(raw))
def size_bytes(value):
    assert 0<=value<2**28
    return bytes((value>>shift)&127 for shift in (21,14,7,0))
def parse(data):
    # These are the actual current file features. Stop safely on other formats.
    assert data[:6]==b'ID3\x04\x00\x00','Expected ordinary ID3v2.4 without extended header/unsynchronisation/footer'
    end=10+decode_size(data[6:10]);assert end<=len(data)
    assert data[-128:-125]!=b'TAG','Legacy ID3v1 requires a separate migration; file left untouched'
    frames=[];pos=10
    while pos<end and data[pos]!=0:
        assert pos+10<=end
        name=data[pos:pos+4].decode('ascii');assert re.fullmatch('[A-Z0-9]{4}',name)
        length=decode_size(data[pos+4:pos+8]);stop=pos+10+length;assert stop<=end
        frames.append((name,data[pos:stop]));pos=stop
    assert not any(data[pos:end]),'Unexpected nonzero tag padding'
    return frames,data[end:],end
def text_frame(name,value):
    payload=b'\x03'+value.encode('utf-8')+b'\x00'
    return name.encode('ascii')+size_bytes(len(payload))+b'\x00\x00'+payload
def tag_values(path):
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format_tags','-of','json',str(path)],capture_output=True,text=True,encoding='utf-8',check=True)
    return json.loads(result.stdout)['format'].get('tags',{})
def essence(path):
    # Copy encoded MP3 packets into FFmpeg's hash muxer; no decoding/re-encoding.
    result=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],capture_output=True,text=True,check=True)
    return result.stdout.strip().split('=',1)[1]
def title_for(path,config):
    return ' - '.join(x for x in (config['title_base'],config.get('draft_label'),path.stem) if x)
def update_data(data,expected):
    before,audio,old_end=parse(data)
    values={'TIT2':expected['title'],'TPE1':expected['artist'],'TALB':expected['album']}
    done=set();frames=[]
    for name,raw in before:
        if name in TARGETS:
            if name not in done:frames.append(text_frame(name,values[name]));done.add(name)
        else:frames.append(raw)
    for name in ('TIT2','TPE1','TALB'):
        if name not in done:frames.append(text_frame(name,values[name]))
    body=b''.join(frames)
    # Preserve the original tag extent where possible. Otherwise add only padding.
    new_size=max(old_end-10,len(body)+32)
    assert not any(name=='CHAP' for name,_ in before) or new_size==old_end-10,'Chapter byte offsets require a dedicated update; file left untouched'
    output=data[:6]+size_bytes(new_size)+body+bytes(new_size-len(body))+audio
    after,new_audio,_=parse(output)
    assert [(n,b) for n,b in before if n not in TARGETS]==[(n,b) for n,b in after if n not in TARGETS]
    assert audio==new_audio
    return output,sha(audio),[name for name,_ in before]

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apply',action='store_true')
parser.add_argument('--resume',type=Path)
args=parser.parse_args()
config=json.loads((P/'chapter-metadata-defaults.json').read_text(encoding='utf-8'))
manifest_path=P/'manifest.json' if (P/'manifest.json').exists() else P/'release-manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
files=[]
for c in manifest['chapters']:
    root=(P/c['file']).resolve();assert root.parent==P and re.match(r'^\d{2} - ',root.name)
    files.append(root)
    mobile=P/'mobile'/root.name
    if mobile.is_file():files.append(mobile)
assert len(set(files))==len(files) and len(files)>=len(manifest['chapters'])
assert all(f.is_file() for f in files)
if args.resume:
    run=args.resume.resolve();report=json.loads((run/'report.json').read_text(encoding='utf-8'))
    assert report['root']==str(P) and report['config']==config
else:
    edition=re.sub(r'[^A-Za-z0-9_-]+','-',config.get('draft_label') or 'Final').strip('-')
    run=P.parent/'Audiobook Metadata Backups'/(datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')+'-'+edition+'-tags')
    assert not run.exists();run.mkdir(parents=True)
    report={'root':str(P),'config':config,'run_directory':str(run),'status':'staging','records':[],'errors':[],'excluded_files':{r['file']:hashlib.sha256(Path(r['file']).read_bytes()).hexdigest() for r in manifest['combined']+manifest['mobile_parts']}}
    for f in [manifest_path,P/'mobile'/'manifest.json',P/'chapter-manifest.csv',*list((P/'working').glob('*-final.json')),*list((P/'working').glob('*-chapter.json'))]:
        if not f.exists():continue
        dest=run/'metadata-before'/f.relative_to(P);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    def stage(path):
        relative=path.relative_to(P);original=path.read_bytes()
        expected={'title':title_for(path,config),'artist':config['artist'],'album':config['album']}
        output,audio_hash,frame_ids=update_data(original,expected)
        old=run/'originals'/relative;new=run/'staged'/relative
        old.parent.mkdir(parents=True,exist_ok=True);new.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,old);new.write_bytes(output)
        assert sha(original)==sha(old.read_bytes())
        before_hash=essence(old);after_hash=essence(new);assert before_hash==after_hash
        actual=tag_values(new)
        assert all(actual.get(k)==v for k,v in expected.items()),(str(path),actual)
        return {'file':str(path),'relative':str(relative),'backup':str(old),'staged':str(new),'before_file_sha256':sha(original),'after_file_sha256':sha(output),'audio_essence_sha256_before':before_hash,'audio_essence_sha256_after':after_hash,'audio_payload_sha256':audio_hash,'other_frames_preserved_byte_for_byte':True,'original_frame_ids':frame_ids,'expected_tags':expected,'verified_tags':actual,'bytes_after':len(output),'status':'staged_verified'}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(stage,path):path for path in files}
        for future in as_completed(futures):
            try:report['records'].append(future.result())
            except Exception as error:report['errors'].append({'file':str(futures[future]),'error':str(error)})
    report['records'].sort(key=lambda r:r['relative'])
    report['status']='staged_verified' if not report['errors'] else 'staging_failed'
    save(run/'report.json',report)
    if report['errors']:raise RuntimeError(json.dumps(report['errors']))

if args.apply:
    for r in report['records']:
        target,stage=Path(r['file']),Path(r['staged'])
        current=sha(target.read_bytes())
        if current==r['after_file_sha256']:r['status']='applied';continue
        assert current==r['before_file_sha256'],'File changed since staging: '+str(target)
        try:
            os.replace(stage,target)
            assert sha(target.read_bytes())==r['after_file_sha256']
            actual=tag_values(target);assert all(actual.get(k)==v for k,v in r['expected_tags'].items())
            assert sha(parse(target.read_bytes())[1])==r['audio_payload_sha256']
            r['status']='applied'
        except PermissionError as error:
            r['status']='staged_locked';r['lock_error']=str(error)
        save(run/'report.json',report)
    applied={r['file']:r for r in report['records'] if r['status']=='applied'}
    for c in manifest['chapters']:
        key=str((P/c['file']).resolve())
        if key in applied:
            r=applied[key];c.update(mp3_sha256=r['after_file_sha256'],mp3_bytes=r['bytes_after'],mp3_tags=r['expected_tags'],mp3_audio_essence_sha256=r['audio_essence_sha256_after'])
            for suffix in ('final','chapter'):
                f=P/'working'/f'{c["index"]:02d}-{suffix}.json'
                if f.exists():
                    data=json.loads(f.read_text(encoding='utf-8'));data.update(mp3_sha256=r['after_file_sha256'],mp3_bytes=r['bytes_after'],mp3_tags=r['expected_tags'],mp3_audio_essence_sha256=r['audio_essence_sha256_after']);save(f,data)
    phone_path=P/'mobile'/'manifest.json'
    phone=json.loads(phone_path.read_text(encoding='utf-8')) if phone_path.exists() else {'chapters':[]}
    for c in phone['chapters']:
        path=str(P/'mobile'/c['file'])
        if path in applied:
            r=applied[path];c.update(sha256=r['after_file_sha256'],bytes=r['bytes_after'],tags=r['expected_tags'],audio_essence_sha256=r['audio_essence_sha256_after'])
    if phone_path.exists():save(phone_path,phone)
    for file,expected in report['excluded_files'].items():assert sha(Path(file).read_bytes())==expected,'Excluded file changed: '+file
    report['applied_count']=len(applied);report['pending_count']=len(files)-len(applied)
    report['status']='complete' if not report['pending_count'] else 'partially_applied_locked_files_preserved'
    report['audio_reencoded']=False;report['no_applications_closed']=True
    manifest['chapter_metadata']={'defaults_file':'chapter-metadata-defaults.json','config':config,'applied_count':len(applied),'pending_count':report['pending_count'],'audio_essence_unchanged':True,'backup_and_restore_directory':str(run),'report':'chapter-metadata-report.json'}
    save(manifest_path,manifest)
    portable=P/'release-manifest.json'
    if portable!=manifest_path and portable.exists():
        data=json.loads(portable.read_text(encoding='utf-8'))
        for c in data['chapters']:
            r=applied.get(str((P/c['file']).resolve()))
            if r:c.update(mp3_sha256=r['after_file_sha256'],mp3_bytes=r['bytes_after'],mp3_tags=r['expected_tags'],mp3_audio_essence_sha256=r['audio_essence_sha256_after'])
        save(portable,data)
    csv_path=P/'chapter-manifest.csv'
    with csv_path.open(encoding='utf-8-sig',newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    for row in rows:
        file=str(P/row['mp3'])
        if file in applied:row['sha256']=applied[file]['after_file_sha256']
    with csv_path.open('w',encoding='utf-8-sig',newline='') as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    save(P/'chapter-metadata-report.json',report)
save(run/'report.json',report)
print(json.dumps({'status':report['status'],'applied':report.get('applied_count',0),'pending':report.get('pending_count',len(files)),'backup':str(run),'sample_title':report['records'][0]['expected_tags']['title'],'audio_essence_equal':all(r['audio_essence_sha256_before']==r['audio_essence_sha256_after'] for r in report['records'])},ensure_ascii=False),flush=True)

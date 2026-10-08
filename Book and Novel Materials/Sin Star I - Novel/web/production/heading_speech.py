"""Generate only existing section labels/titles with the accepted Michael voice."""
from pathlib import Path
import argparse,json,os,subprocess,hashlib

def main():
    p=argparse.ArgumentParser();p.add_argument('--book',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--only',type=int);a=p.parse_args()
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HOME=str(a.model.parents[3]),PYTHONDONTWRITEBYTECODE='1')
    import numpy as np
    import soundfile as sf
    import torch
    from kokoro import KModel,KPipeline
    torch.manual_seed(421);torch.set_num_threads(4)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    model=KModel(repo_id='hexgrad/Kokoro-82M',config=str(a.model/'config.json'),model=str(a.model/'kokoro-v1_0.pth')).to(device).eval()
    pipe=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',model=model,device=device)
    voice=torch.load(a.model/'voices/am_michael.pt',weights_only=True)
    chapters=json.loads(a.book.read_text(encoding='utf8'))['chapters'][1:]
    a.output.mkdir(parents=True,exist_ok=True);records=[];rate=24000
    for index,c in enumerate(chapters):
        if a.only is not None and index!=a.only:continue
        recordfile=a.output/f'{index:02d}.json'
        if recordfile.exists():
            old=json.loads(recordfile.read_text(encoding='utf8'));assert old['label']==c['label'] and old['title']==c['title']
            assert old['model_revision']==a.model.name and old['voice']=='am_michael' and old['speed']==.97 and old['seed']==421
            assert hashlib.sha256((a.output/old['file']).read_bytes()).hexdigest()==old['sha256']
            records.append(old);continue
        pieces=[];speech=[]
        for text in [c['label'],c['title']]:
            generated=list(pipe(text+'.',voice=voice,speed=.97));wave=np.concatenate([x.audio.cpu().numpy() for x in generated])
            active=np.flatnonzero(np.abs(wave)>.001);assert len(active)
            lo=max(0,int(active[0])-.05*rate);hi=min(len(wave),int(active[-1])+1+.10*rate)
            wave=wave[int(lo):int(hi)];pieces.append(wave)
            speech.append({'text':text,'phonemes':' '.join(x.phonemes for x in generated),'samples':len(wave)})
        lead=np.zeros(round(.12*rate));between=np.zeros(round(.55*rate));tail=np.zeros(round(.80*rate))
        prefix=np.concatenate([lead,pieces[0],between,pieces[1],tail]).astype('float32')
        raw=a.output/f'{index:02d}-raw.wav';out=a.output/f'{index:02d}-heading.wav';sf.write(raw,prefix,rate,subtype='PCM_24')
        measured=subprocess.run(['ffmpeg','-v','info','-i',str(raw),'-af','loudnorm=I=-19.5:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf8',check=True).stderr
        values=json.JSONDecoder().raw_decode(measured[measured.rfind('{'):])[0];gain=10**((-19.5-float(values['input_i']))/20);gain=min(gain,.794/max(float(np.max(np.abs(prefix))),1e-9))
        sf.write(out,prefix*gain,rate,subtype='PCM_24')
        label_start=len(lead)/rate;label_end=label_start+len(pieces[0])/rate;title_start=label_end+len(between)/rate;title_end=title_start+len(pieces[1])/rate
        record={'index':index,'chapterId':c['id'],'label':c['label'],'title':c['title'],'voice':'am_michael','model_revision':a.model.name,'speed':.97,'seed':421,'device':device,'sample_rate':rate,'file':out.name,'samples':len(prefix),'bodyStart':len(prefix)/rate,'labelStart':label_start,'labelEnd':label_end,'titleStart':title_start,'titleEnd':title_end,'pause_between_seconds':.55,'pause_before_body_seconds':.8,'gain':gain,'speech':speech,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
        recordfile.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8');records.append(record)
        print(json.dumps({'ready':str(out),'chapter':c['id'],'bodyStart':record['bodyStart']}),flush=True)
    (a.output/'manifest.json').write_text(json.dumps({'voice':'am_michael','only_heading_synthesis':True,'records':records},ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()

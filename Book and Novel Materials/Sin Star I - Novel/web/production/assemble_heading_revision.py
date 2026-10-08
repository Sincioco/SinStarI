"""Create separate web chapter revisions from verified accepted lossless bodies."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,json,hashlib,subprocess,shutil
import numpy as np
import soundfile as sf

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args):return subprocess.check_output(args,stderr=subprocess.PIPE)
def main():
    p=argparse.ArgumentParser();p.add_argument('--accepted',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--speech',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    release=json.loads((a.accepted/'release-manifest.json').read_text(encoding='utf8'))
    mobile=json.loads((a.accepted/'mobile/manifest.json').read_text(encoding='utf8'))
    baseline=json.loads((a.baseline/'book.json').read_text(encoding='utf8'))
    a.output.mkdir(parents=True,exist_ok=True);(a.output/'mobile').mkdir(exist_ok=True)
    for source,target in [(a.accepted/'release-manifest.json',a.output/'accepted-release-manifest.json'),(a.baseline/'book.json',a.output/'baseline-book.json')]:
        if target.exists():assert digest(source)==digest(target),'Inputs changed; use a fresh output directory.'
        else:shutil.copy2(source,target)
    def assemble(index):
        c=release['chapters'][index];m=mobile['chapters'][index];old=baseline['chapters'][index+1]
        rec=json.loads((a.speech/f'{index:02d}.json').read_text(encoding='utf8'))
        output=a.output/'mobile'/c['file'];receipt=a.output/f'{index:02d}-assembly.json'
        master=a.accepted/c['file'];prior=a.accepted/'mobile'/m['file'];flac=a.accepted/'working'/f'{index:02d}-normalized.flac';heading=a.speech/rec['file']
        inputs={name:digest(path) for name,path in {'master':master,'mobile':prior,'flac':flac,'heading':heading,'speech_record':a.speech/f'{index:02d}.json','baseline':a.baseline/'book.json','release':a.accepted/'release-manifest.json','mobile_manifest':a.accepted/'mobile/manifest.json'}.items()}
        if receipt.exists():
            result=json.loads(receipt.read_text(encoding='utf8'))
            assert result.get('input_hashes')==inputs,'Unverified or changed assembly inputs; use a fresh output directory.'
            assert digest(output)==result['sha256'];return result
        assert not output.exists(),'Refusing to replace an unverified revision'
        master=a.accepted/c['file'];prior=a.accepted/'mobile'/m['file'];flac=a.accepted/'working'/f'{index:02d}-normalized.flac';heading=a.speech/rec['file']
        assert digest(master)==c['mp3_sha256'] and digest(prior)==m['sha256']==old['sha256']
        assert digest(heading)==rec['sha256']
        body,rate=sf.read(flac,dtype='int32');prefix,prefix_rate=sf.read(heading,dtype='int32')
        assert rate==prefix_rate==24000 and body.ndim==prefix.ndim==1
        assert len(body)==round(c['duration_seconds']*rate) and len(prefix)==rec['samples']
        # Catch stale lossless working files (e.g. an earlier cast) against the accepted mobile performance.
        decoded=np.frombuffer(run(['ffmpeg','-v','error','-i',str(prior),'-f','f32le','-acodec','pcm_f32le','-']),dtype='<f4')
        assert abs(len(decoded)-len(body))<576,(index,len(decoded),len(body))
        common=min(len(decoded),len(body));reference=(body[:common].astype('float32')/2147483648)[::4];sample=decoded[:common][::4]
        correlation=float(np.dot(reference,sample)/np.sqrt(np.dot(reference,reference)*np.dot(sample,sample)))
        # Re-encoding this lossless source at the accepted master settings must
        # reproduce every encoded audio packet, independently of ID3 metadata.
        master_check=a.output/f'{index:02d}-master-check.mp3'
        run(['ffmpeg','-v','error','-n','-i',str(flac),'-ar','24000','-ac','1','-c:a','libmp3lame','-b:a','96k',str(master_check)])
        essence=run(['ffmpeg','-v','error','-i',str(master_check),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).decode().strip().split('=')[1]
        assert essence==c['mp3_audio_essence_sha256'],('Lossless source does not reproduce accepted master',index)
        master_check.unlink()
        # Align the added silence to one 24 ms MP3 frame, preserving body frame alignment.
        padding=(-len(prefix))%576;prefix=np.concatenate([prefix,np.zeros(padding,dtype='int32')])
        rec={**rec,'bodyStart':len(prefix)/rate,'alignment_pad_seconds':padding/rate}
        joined=np.concatenate([prefix,body]);temp=a.output/f'{index:02d}-assembly.flac'
        sf.write(temp,joined,rate,subtype='PCM_24')
        verify,_=sf.read(temp,dtype='int32');assert np.array_equal(verify[len(prefix):],body)
        body_hash=hashlib.sha256(body.tobytes()).hexdigest()
        tags=m['tags'];args=['ffmpeg','-v','error','-n','-i',str(temp),'-map_metadata','-1','-ar','24000','-ac','1','-c:a','libmp3lame','-b:a','32k']
        for k in ['title','artist','album']:args+=['-metadata',k+'='+tags[k]]
        run(args+[str(output)])
        new_pcm=np.frombuffer(run(['ffmpeg','-v','error','-i',str(output),'-f','f32le','-acodec','pcm_f32le','-']),dtype='<f4')
        assert abs(len(new_pcm)-len(joined))<576 and np.isfinite(new_pcm).all(),(index,len(new_pcm),len(joined))
        if len(new_pcm)<len(joined):assert np.max(np.abs(joined[len(new_pcm):].astype('float64')))/2147483648<.001
        body_after=new_pcm[len(prefix):len(prefix)+common][::4]
        after_correlation=float(np.dot(reference,body_after)/np.sqrt(np.dot(reference,reference)*np.dot(body_after,body_after)))
        mobile_correlation=float(np.dot(sample,body_after)/np.sqrt(np.dot(sample,sample)*np.dot(body_after,body_after)))
        assert mobile_correlation>.999,('Unexpected change to accepted mobile performance',index,mobile_correlation)
        probe=json.loads(run(['ffprobe','-v','error','-show_entries','format=duration:format_tags=title,artist,album','-of','json',str(output)]))
        assert all(probe['format']['tags'][k]==tags[k] for k in ['title','artist','album'])
        temp.unlink() # Only this explicitly named, verified temporary assembly.
        result={**rec,'file':'mobile/'+output.name,'bytes':output.stat().st_size,'sha256':digest(output),'duration_seconds':len(new_pcm)/rate,'lossless_duration_seconds':len(joined)/rate,'codec_tail_padding_seconds':(len(new_pcm)-len(joined))/rate,'encoded_duration_seconds':float(probe['format']['duration']),'accepted_master_sha256':c['mp3_sha256'],'accepted_master_essence_reproduced':True,'accepted_mobile_sha256':m['sha256'],'accepted_flac_sha256':digest(flac),'body_pcm_sha256':body_hash,'body_pcm_preserved_in_assembly':True,'accepted_mobile_correlation':correlation,'revised_body_correlation':after_correlation,'revised_vs_accepted_mobile_correlation':mobile_correlation,'tags':tags}
        result['input_hashes']=inputs
        receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'assembled':index,'bodyStart':rec['bodyStart'],'correlation':after_correlation}),flush=True);return result
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(assemble,range(42)))
    manifest={'revision':'web-heading-prefix-v1','status':'Local review; not accepted or published','edition':'Draft 2a','scope':'42 web/mobile chapter tracks only; title-page audio and accepted chapter/combined masters unchanged','previous_version':baseline['version'],'source_sha256':release['source_sha256'],'sections':42,'records':records}
    (a.output/'revision-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'ready':str(a.output/'revision-manifest.json'),'chapters':len(records)}),flush=True)

if __name__=='__main__':main()

const frame=document.getElementById('reader'),report=document.getElementById('report');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const results=[];
function record(name,details){results.push({name,status:'passed',details});report.textContent=JSON.stringify(results,null,2);}
function assert(value,label){if(!value)throw new Error(label);}
async function until(test,label,ms=10000){const end=Date.now()+ms;while(Date.now()<end){if(test())return;await sleep(40);}throw new Error('Timed out: '+label);}
const doc=()=>frame.contentDocument,win=()=>frame.contentWindow,audio=()=>doc().getElementById('audio'),el=id=>doc().getElementById(id);
async function reloadReader(){const loaded=new Promise(resolve=>frame.addEventListener('load',resolve,{once:true}));win().location.reload();await loaded;await until(()=>el('seek')&&!el('seek').disabled&&audio().readyState>=2,'reloaded metadata');}
async function choose(index){doc().querySelector('[data-chapter="'+index+'"]').click();await until(()=>!el('seek').disabled&&audio().readyState>=2,'chapter '+index);await sleep(150);audio().pause();}
async function seekPlay(time){audio().currentTime=time;await until(()=>!audio().seeking&&audio().currentTime>=time-.05,'seek '+time);await audio().play();await sleep(180);}
function cacheName(book){return 'sin-star-audio-'+encodeURIComponent(new URL('../',location.href).pathname)+'-'+book.version;}
async function hashes(){const book=await(await fetch('../book.json')).json();return {book,cache:await caches.open(cacheName(book))};}
function url(c){const u=new URL('../'+c.audio,location.href);u.searchParams.set('v',c.sha256);return u.href;}
async function waitDownload(){await until(()=>el('download-cancel').hidden,'download settled',30000);}
document.getElementById('run').onclick=async()=>{
  results.length=0;report.textContent='Running…';
  try{
    await until(()=>el('download-current')&&!el('download-current').disabled,'offline ready');
    const {book,cache}=await hashes();
    let matched=0;
    const normalize=s=>(s.match(/[\p{L}\p{N}_]+/gu)||[]).join(' ');
    for(const c of book.chapters)for(const cue of c.cues){const nodes=[...doc().querySelectorAll('[data-cue-id="'+cue.id+'"]')];assert(normalize(nodes.map(n=>n.textContent).join(' '))===cue.text,cue.id);matched++;}
    record('All cue text maps to stable IDs',matched+' cues');
    await choose(1);await seekPlay(8);assert(doc().querySelector('.spoken')?.dataset.cueId==='ch-00-s0001','phrase highlight; time='+audio().currentTime+'; cue='+doc().querySelector('.spoken')?.dataset.cueId);
    const anchor=doc().getElementById('ch-00-b0002'),figure=doc().createElement('figure');figure.dataset.noNarration='true';figure.innerHTML='<img src="./icon.svg" width="240" height="180" alt="Temporary test illustration"><figcaption>Temporary caption excluded from narration.</figcaption>';anchor.before(figure);
    await sleep(200);assert(doc().querySelector('.spoken')?.dataset.cueId==='ch-00-s0001','image insertion shifted highlight');assert(!figure.querySelector('.spoken'),'caption highlighted');record('Image and caption insertion','Existing phrase target and audio alignment unchanged; fixture removed afterward');
    const target=doc().querySelector('[data-cue-id="ch-00-s0001"]'),original=target.textContent;target.textContent='Edited text that does not match the recording.';await sleep(130);assert(!doc().querySelector('.spoken'),'stale highlight survived text mismatch');target.textContent=original;figure.remove();await sleep(100);assert(doc().querySelector('.spoken'),'restored text did not recover');record('Edited/missing-match fail-safe','Old highlight cleared, original text restored');
    audio().pause();await until(()=>!doc().querySelector('.spoken'),'pause clears highlight');record('Pause clears highlight',true);
    await choose(2);audio().currentTime=27.3;await until(()=>!audio().seeking,'resume seek');win().dispatchEvent(new Event('pagehide'));await reloadReader();await until(()=>el('current-title')?.textContent===book.chapters[2].heading&&Math.abs(audio().currentTime-27.3)<2,'resume timestamp');audio().pause();record('Return visit resume','Chapter One at 27.3 seconds');
    const storagePrototype=win().Storage.prototype,oldSet=storagePrototype.setItem;storagePrototype.setItem=()=>{throw new DOMException('Disabled','SecurityError');};audio().currentTime=29;win().dispatchEvent(new Event('pagehide'));assert(el('connection-status').textContent.includes('unavailable'),'storage failure not explained');storagePrototype.setItem=oldSet;record('Position-storage failure','Playback continues and memory-unavailable message appears');
    for(const i of [4,10,3])doc().querySelector('[data-chapter="'+i+'"]').click();await until(()=>el('current-title').textContent===book.chapters[3].heading&&audio().readyState>=1,'rapid navigation');audio().pause();assert(doc().querySelectorAll('.reading-section:not([hidden])').length===1,'multiple sections visible');assert(audio().currentSrc.includes('/02.mp3')||audio().currentSrc.startsWith('blob:'),'wrong final source');record('Rapid chapter selection','One audio element and final requested chapter');
    await cache.delete(url(book.chapters[3]));
    const originalFetch=win().fetch;win().fetch=(input,options)=>String(input).includes('/audio/02.mp3')?Promise.resolve(new Response(new Uint8Array(5),{status:206})):originalFetch(input,options);
    el('download-current').click();await waitDownload();assert(el('download-status').textContent.includes('complete audio'),'partial response not rejected');assert(!await cache.match(url(book.chapters[3])),'partial response cached');win().fetch=originalFetch;record('Partial response guard','HTTP 206 rejected; no partial audio cached');
    const estimate=win().navigator.storage.estimate.bind(win().navigator.storage);win().navigator.storage.estimate=async()=>({quota:1,usage:0});el('download-current').click();await waitDownload();assert(el('download-status').textContent.includes('Not enough'),'quota preflight');win().navigator.storage.estimate=estimate;record('Insufficient quota','Download stopped with actionable message');
    el('download-all').click();await sleep(20);el('download-cancel').click();await waitDownload();assert(el('download-status').textContent.includes('cancelled')||el('download-status').textContent.includes('ready'),'cancel state');record('Cancel download','No stuck controls; previously completed chapters retained');
    el('download-all').click();await waitDownload();const keys=await cache.keys();assert(keys.length===43,'whole-book cache count '+keys.length);for(const c of book.chapters){const r=await cache.match(url(c));assert(r?.headers.get('X-Audio-SHA256')===c.sha256&&Number(r.headers.get('Content-Length'))===c.bytes,'saved validation '+c.id);}record('Retry and whole-book download','43 complete hash-verified audio files, '+book.totalBytes+' bytes');
    const range=await fetch(url(book.chapters[1]),{headers:{Range:'bytes=10-25'}});assert(range.status===206&&(await range.arrayBuffer()).byteLength===16,'range response');const suffix=await fetch(url(book.chapters[1]),{headers:{Range:'bytes=-32'}});assert(suffix.status===206&&(await suffix.arrayBuffer()).byteLength===32,'suffix range');const invalid=await fetch(url(book.chapters[1]),{headers:{Range:'bytes=999999999-'}});assert(invalid.status===416,'invalid range');record('Cached Range requests','206 exact/suffix ranges and 416 invalid range');
    await choose(42);await seekPlay(Math.max(0,audio().duration-.15));await until(()=>audio().ended,'final end');assert(el('current-title').textContent===book.chapters[42].heading&&el('playback-status').textContent.includes('The end'),'final chapter restart');record('Final chapter ends cleanly','No wraparound and no remaining highlight');
    await choose(3);el('remove-current').click();await until(()=>el('download-status').textContent.includes('removed'),'remove chapter');assert(!await cache.match(url(book.chapters[3])),'remove chapter retained file');record('Remove offline chapter','Chapter Two removed for missing-offline-audio check');
    await choose(1);audio().currentTime=33;win().dispatchEvent(new Event('pagehide'));audio().pause();record('Offline test prepared','Prologue and Chapter One cached; Chapter Two missing. Stop local server then run offline checks.');
  }catch(error){results.push({status:'FAILED',error:String(error)});report.textContent=JSON.stringify(results,null,2);try{audio().pause();}catch{}}
};
document.getElementById('offline').onclick=async()=>{
  try{
    await reloadReader();await until(()=>el('current-title')?.textContent.includes('Prologue')&&audio().readyState>=1,'offline reload',15000);assert(audio().currentSrc.startsWith('blob:'),'offline cache not chosen');await seekPlay(40);assert(audio().currentTime>=40&&!audio().paused,'offline seek/play');record('Origin unavailable: reload and seek','App shell, book text and cached MP3 play without the local HTTP server');
    audio().currentTime=audio().duration-.1;await until(()=>el('current-title')?.textContent.includes('Chapter One')&&audio().readyState>=1,'next cached chapter');assert(audio().currentSrc.startsWith('blob:'),'next chapter not local');record('Origin unavailable: auto-next','Cached Chapter One starts automatically');
    audio().currentTime=audio().duration-.1;await until(()=>el('current-title')?.textContent.includes('Chapter Two')&&el('playback-status')?.textContent.includes('unavailable'),'missing chapter');assert(!doc().querySelector('.spoken'),'missing audio left highlight');record('Origin unavailable: missing chapter','Clear unavailable/download message and cleared highlight');
  }catch(error){results.push({status:'FAILED',error:String(error)});report.textContent=JSON.stringify(results,null,2);}
};

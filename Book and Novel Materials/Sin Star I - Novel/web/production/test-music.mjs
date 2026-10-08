import fs from 'node:fs';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../music.js',import.meta.url),'utf8').replace(/^import .*;\r?\n/,'const musicBytes=null, musicSaved=async tracks=>tracks.map(()=>false), downloadMusic=async()=>{}, removeMusic=async()=>{};\n');
const {initMusic}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
class E {events={};paused=true;ended=false;textContent='';value='';addEventListener(n,f){(this.events[n]??=[]).push(f);}setAttribute(n,v){this[n]=v;}fire(n){for(const f of this.events[n]||[])f({});}}
const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
const tracks=[{title:'Horizon'},{title:'March'},{title:'Bloom'}],results=[];
function setup(load=async track=>track.title,settings=null) {
 const audio=new E(), nodes=new Map(), contexts=[];
 const get=id=>{if(!nodes.has(id))nodes.set(id,new E());return nodes.get(id);};
 globalThis.window=new E();globalThis.localStorage={getItem:()=>JSON.stringify(settings),setItem(){}};
 globalThis.fetch=async()=>({ok:true,json:async()=>({tracks})});
 class Context extends E {
  state='suspended';currentTime=0;sources=[];
  constructor(){super();contexts.push(this);}
  createGain(){return this.gain={gain:{value:0,setValueAtTime(v){this.value=v;}},connect(){}};}
  resume(){this.state='running';return Promise.resolve();}
  decodeAudioData(title){return Promise.resolve({title,duration:160});}
  createBufferSource(){const s={connect(){},disconnect(){},start(when,offset){this.offset=offset;this.live=true;},stop(){this.live=false;},end(){this.live=false;this.onended?.();}};this.sources.push(s);return s;}
 }
 const music=initMusic({audio,get,Context,load});
 return {audio,get,contexts,music,playing(){audio.paused=false;audio.fire('playing');},pause(){audio.paused=true;audio.fire('pause');}};
}
async function test(name,fn){await fn();results.push({name,passed:true});}
await test('No audio context until gesture; initial gain 8%',async()=>{
 const s=setup();await s.music.ready;s.playing();await flush();assert.equal(s.contexts.length,0);
 s.music.gesture();await flush();assert.equal(s.contexts[0].gain.gain.value,.08);assert.equal(s.contexts[0].sources[0].buffer.title,'Horizon');
});
await test('An existing user volume/mute preference survives the new default',async()=>{
 const s=setup(undefined,{volume:.31,muted:true});await s.music.ready;
 assert.equal(s.get('music-volume').value,'31');assert.equal(s.get('music-mute')['aria-pressed'],'true');
 s.music.gesture();await flush();assert.equal(s.contexts[0].gain.gain.value,0);
});
await test('Enable while paused confirms readiness without starting a source',async()=>{
 const s=setup();await s.music.ready;s.get('music-enable').fire('click');await flush();
 assert.equal(s.contexts[0].state,'running');assert.equal(s.contexts[0].sources.length,0);
 assert.equal(s.get('music-enable').textContent,'Music enabled');assert.equal(s.get('music-enable').disabled,true);
 assert.match(s.get('music-status').textContent,/press Play/);
 s.playing();await flush();assert.equal(s.get('music-enable').textContent,'Music playing');
 s.pause();assert.equal(s.get('music-enable').textContent,'Music enabled');assert.match(s.get('music-status').textContent,/press Play/);
});
await test('Enable clears mute and restores 8% when volume is zero',async()=>{
 const s=setup(undefined,{volume:0,muted:true});await s.music.ready;
 s.get('music-enable').fire('click');await flush();
 assert.equal(s.get('music-volume').value,'8');assert.equal(s.get('music-mute')['aria-pressed'],'false');assert.equal(s.contexts[0].gain.gain.value,.08);
});
await test('Playlist advances Horizon → March → Bloom → Horizon without overlapping sources',async()=>{
 const s=setup();await s.music.ready;s.music.gesture();s.playing();await flush();const c=s.contexts[0];
 for(const title of ['Horizon','March','Bloom','Horizon']){assert.equal(c.sources.at(-1).buffer.title,title);assert.equal(c.sources.filter(x=>x.live).length,1);c.sources.at(-1).end();await flush();}
});
await test('Pause and chapter source changes retain track and offset',async()=>{
 const s=setup();await s.music.ready;s.music.gesture();s.playing();await flush();const c=s.contexts[0];
 c.currentTime=24;s.pause();assert.equal(c.sources.filter(x=>x.live).length,0);s.audio.fire('emptied');c.currentTime=70;s.playing();await flush();assert.equal(c.sources.at(-1).offset,24);assert.equal(c.sources.at(-1).buffer.title,'Horizon');
});
await test('Pause while fetch/decode is pending cannot start late music',async()=>{
 let resolve;const s=setup(()=>new Promise(r=>resolve=r));await s.music.ready;s.music.gesture();s.playing();await flush();s.pause();resolve('Horizon');await flush();assert.equal(s.contexts[0].sources.length,0);
});
await test('Mute and zero volume stop music; unmute resumes same position',async()=>{
 const s=setup();await s.music.ready;s.music.gesture();s.playing();await flush();const c=s.contexts[0];c.currentTime=10;
 s.get('music-mute').fire('click');assert.equal(c.gain.gain.value,0);assert.equal(c.sources.filter(x=>x.live).length,0);
 s.get('music-mute').fire('click');await flush();assert.equal(c.sources.at(-1).offset,10);
 s.get('music-volume').value='0';s.get('music-volume').fire('input');await flush();assert.equal(c.sources.filter(x=>x.live).length,0);
});
await test('All missing tracks try once then leave narration alone',async()=>{
 let loads=0;const s=setup(async()=>{loads++;throw new Error('missing');});await s.music.ready;s.music.gesture();s.playing();await flush();assert.equal(s.contexts[0].sources.length,0);assert.equal(s.audio.paused,false);assert.ok(loads<=6);assert.match(s.get('music-status').textContent,/unavailable/);
});
await test('A missing track skips to next available track',async()=>{
 const s=setup(async track=>{if(track.title==='Horizon')throw new Error();return track.title;});await s.music.ready;s.music.gesture();s.playing();await flush();assert.equal(s.contexts[0].sources.at(-1).buffer.title,'March');
});
await test('Browser interruption stops source and waits for a resume gesture',async()=>{
 const s=setup();await s.music.ready;s.music.gesture();s.playing();await flush();const c=s.contexts[0];c.currentTime=14;c.state='interrupted';c.fire('statechange');assert.equal(c.sources.filter(x=>x.live).length,0);assert.match(s.get('music-status').textContent,/resume/);s.music.gesture();await flush();assert.equal(c.sources.at(-1).offset,14);
});
await test('Narration ending stops the playlist',async()=>{
 const s=setup();await s.music.ready;s.music.gesture();s.playing();await flush();s.audio.ended=true;s.audio.fire('ended');assert.equal(s.contexts[0].sources.filter(x=>x.live).length,0);
});
fs.writeFileSync(new URL('./music-unit-validation.json',import.meta.url),JSON.stringify({utc:new Date().toISOString(),passed:results.length,results},null,2));console.log(JSON.stringify({passed:results.length}));

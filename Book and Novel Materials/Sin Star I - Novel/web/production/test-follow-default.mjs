import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const web = process.argv[2] || path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const source = fs.readFileSync(path.join(web,'follow-narration.js'),'utf8');
const {initNarrationFollow} = await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
class Target {
  events = new Map();
  addEventListener(name, callback) { this.events.set(name, callback); }
  fire(name, value = {}) { this.events.get(name)?.(value); }
}
const results = [];
function setup({cue=1600, offset=0, height=844, phone=true, paused=false, cueHeight=31,checked=true,currentTime=0}={}) {
  let frames=[], calls=[], touchY=0;
  const reading = new Target(), checkbox = new Target(), viewport = new Target(), win = new Target();
  checkbox.checked=checked;
  Object.assign(viewport,{offsetTop:offset,height,pageTop:offset,pageLeft:0});
  Object.assign(win,{scrollY:0,scrollX:0,innerHeight:height,visualViewport:viewport});
  win.scrollTo = opts=>{ calls.push(opts);win.scrollY=opts.top-offset;viewport.pageTop=opts.top; };
  globalThis.window=win;
  globalThis.document={scrollingElement:{scrollHeight:5000,clientHeight:844}};
  globalThis.matchMedia=()=>({matches:phone});
  globalThis.requestAnimationFrame=callback=>{frames.push(callback);return frames.length;};
  let observer;
  globalThis.ResizeObserver=class{constructor(callback){observer=callback;}observe(){}};
  const header={getBoundingClientRect:()=>({top:0,bottom:62})};
  const player={getBoundingClientRect:()=>({top:height-222,bottom:height})};
  // A long wrapped inline cue: the full union is 800px, first line only 31px.
  const node={getClientRects:()=>[{top:cue-win.scrollY,bottom:cue-win.scrollY+31,width:340,height:31},...(cueHeight>31?[{top:cue-win.scrollY+31,bottom:cue-win.scrollY+cueHeight,width:340,height:cueHeight-31}]:[])]};
  const audio={paused,currentTime,src:'blob:unchanged-saved-audio'}; let nodes=[node];
  const schedule=initNarrationFollow({reading,checkbox,audio,activeNodes:()=>nodes,header,player});
  function flush(){const callbacks=frames;frames=[];callbacks.forEach(callback=>callback());}
  return {reading,checkbox,viewport,win,audio,calls,schedule,flush,observer,header,player,
    setCue:value=>{cue=value;},clearNodes:()=>{nodes=[];}};
}
function test(name,run){run();results.push({name,passed:true});}
const finger=(x,y,id=1)=>({identifier:id,clientX:x,clientY:y});
test('Long offscreen cue starts below fixed header rather than centering its union',()=>{
 const s=setup({cueHeight:800});s.schedule();s.flush();assert.equal(s.calls[0].top,1522);assert.equal(s.calls[0].behavior,'instant');s.schedule();s.flush();assert.equal(s.calls.length,1);
});
test('Long visible-start cue is lifted above player without hiding its start',()=>{const s=setup({cue:200,cueHeight:800});s.schedule();s.flush();assert.equal(s.calls[0].top,122);s.schedule();s.flush();assert.equal(s.calls.length,1);});
test('Fully visible first cue line causes no movement',()=>{const s=setup({cue:200});s.schedule();s.flush();assert.equal(s.calls.length,0);});
test('Line hidden partly under the player is repositioned',()=>{const s=setup({cue:600});s.schedule();s.flush();assert.equal(s.calls.length,1);});
test('Paused audio and missing cue never move the document',()=>{const s=setup({paused:true});s.schedule();s.flush();s.audio.paused=false;s.clearNodes();s.schedule();s.flush();assert.equal(s.calls.length,0);});
test('Following continues during a held touch and small finger drift',()=>{const s=setup();s.reading.fire('touchstart',{touches:[finger(80,100)]});s.reading.fire('touchmove',{touches:[finger(82,105)]});s.schedule();s.flush();assert.equal(s.calls.length,1);assert.equal(s.checkbox.checked,true);s.setCue(2400);s.schedule();s.flush();assert.equal(s.calls.length,2);});
test('Deliberate vertical swipe leaves Follow checked and following',()=>{const s=setup();s.reading.fire('touchstart',{touches:[finger(80,100)]});s.reading.fire('touchmove',{touches:[finger(81,225)]});s.flush();assert.equal(s.checkbox.checked,true);assert.equal(s.calls.length,1);s.reading.fire('touchend',{touches:[]});s.setCue(2600);s.schedule();s.flush();assert.equal(s.calls.length,2);});
test('Horizontal drift does not disable Follow',()=>{const s=setup();s.reading.fire('touchstart',{touches:[finger(80,100)]});s.reading.fire('touchmove',{touches:[finger(110,105)]});assert.equal(s.checkbox.checked,true);});
test('Pinch and multiple fingers never disable or suspend Follow',()=>{const s=setup();s.reading.fire('touchstart',{touches:[finger(80,100),finger(100,100,2)]});s.reading.fire('touchmove',{touches:[finger(60,100),finger(120,100,2)]});s.flush();assert.equal(s.calls.length,1);assert.equal(s.checkbox.checked,true);s.setCue(2200);s.reading.fire('touchend',{touches:[finger(80,100)]});s.flush();assert.equal(s.calls.length,2);assert.equal(s.checkbox.checked,true);});
test('Touch cancellation leaves continuous following enabled',()=>{const s=setup();s.reading.fire('touchstart',{touches:[finger(80,100)]});s.reading.fire('touchcancel',{touches:[]});s.flush();assert.equal(s.calls.length,1);assert.equal(s.checkbox.checked,true);});
test('Vertical and horizontal wheel keep Follow checked and follow new cues',()=>{const s=setup();s.reading.fire('wheel',{deltaY:0,deltaX:20});s.flush();assert.equal(s.calls.length,1);s.setCue(2500);s.reading.fire('wheel',{deltaY:120});s.flush();assert.equal(s.checkbox.checked,true);assert.equal(s.calls.length,2);});
test('Visual viewport resize follows the same cue above raised player',()=>{const s=setup({cue:550});s.schedule();s.flush();assert.equal(s.calls.length,0);s.viewport.height=620;s.player.getBoundingClientRect=()=>({top:398,bottom:620});s.viewport.fire('resize');s.flush();assert.equal(s.calls.length,1);});
test('Nonzero visual viewport offset uses coordinated pageTop',()=>{const s=setup({offset:100});s.schedule();s.flush();assert.equal(s.calls[0].top,1584);});
test('Document boundaries clamp a requested scroll',()=>{const s=setup({cue:6000});s.schedule();s.flush();assert.equal(s.calls[0].top,4156);s.schedule();s.flush();assert.equal(s.calls.length,1);});
test('No usable viewport leaves scroll unchanged',()=>{const s=setup({height:250});s.schedule();s.flush();assert.equal(s.calls.length,0);});
test('Resize checks coalesce and desktop keeps smooth movement',()=>{const s=setup({phone:false});s.schedule();s.observer();s.win.fire('resize');s.flush();assert.equal(s.calls.length,1);assert.equal(s.calls[0].behavior,'smooth');});

test('Fresh visit starts with Follow checked',()=>{const s=setup();assert.equal(s.checkbox.checked,true);s.schedule();s.flush();assert.equal(s.calls.length,1);});
test('Previously restored unchecked form state is reset during initialization',()=>{const s=setup({checked:false});assert.equal(s.checkbox.checked,true);s.flush();assert.equal(s.calls.length,1);});
test('Late form restoration is reset at normal pageshow',()=>{const s=setup();s.checkbox.checked=false;s.win.fire('pageshow',{persisted:false});s.flush();assert.equal(s.checkbox.checked,true);assert.equal(s.calls.length,1);});
test('Back-forward restored page enables Follow without changing audio',()=>{const s=setup({currentTime:27.3});s.checkbox.checked=false;s.checkbox.fire('change');s.win.fire('pageshow',{persisted:true});s.flush();assert.equal(s.checkbox.checked,true);assert.equal(s.calls.length,1);assert.equal(s.audio.currentTime,27.3);assert.equal(s.audio.src,'blob:unchanged-saved-audio');});
test('Checkbox opt-out survives new cues, resume and viewport changes in this visit',()=>{const s=setup();s.checkbox.checked=false;s.checkbox.fire('change');s.flush();s.setCue(2000);s.audio.paused=true;s.schedule();s.flush();s.audio.paused=false;s.schedule();s.win.fire('resize');s.win.fire('orientationchange');s.viewport.fire('resize');s.flush();assert.equal(s.checkbox.checked,false);assert.equal(s.calls.length,0);});
test('Cue tap while manually disabled does not re-enable following',()=>{const s=setup();s.checkbox.checked=false;s.checkbox.fire('change');s.reading.fire('touchstart',{touches:[finger(60,200)]});s.reading.fire('touchmove',{touches:[finger(62,205)]});s.setCue(2100);s.schedule();s.reading.fire('touchend',{touches:[]});s.flush();assert.equal(s.checkbox.checked,false);assert.equal(s.calls.length,0);});
test('Returning from a hidden tab without navigation preserves manual opt-out',()=>{const s=setup();s.checkbox.checked=false;s.win.fire('visibilitychange');s.schedule();s.flush();assert.equal(s.checkbox.checked,false);assert.equal(s.calls.length,0);});
test('Starting Follow does not change paused/resumed timestamp or audio source',()=>{const s=setup({checked:false,paused:true,currentTime:137.25});s.win.fire('pageshow');s.flush();assert.equal(s.audio.paused,true);assert.equal(s.audio.currentTime,137.25);assert.equal(s.calls.length,0);s.audio.paused=false;s.schedule();s.flush();assert.equal(s.audio.currentTime,137.25);assert.equal(s.audio.src,'blob:unchanged-saved-audio');assert.equal(s.calls.length,1);});

// Execute the real app startup/resume block with storage and playback seams.
// This verifies the real saved-position decoder without native browser playback.
const app=fs.readFileSync(path.join(web,'app.js'),'utf8').replace(/\r\n/g,'\n');
const book=JSON.parse(fs.readFileSync(path.join(web,'book.json'),'utf8'));
const startup=app.slice(app.lastIndexOf('\ntry {\n  const response=await fetch'));
assert.ok(startup.startsWith('\ntry {'));
const key=book.identity+'-position-v1';
async function resumeCase(name,saved,wantedIndex,wantedTime){
 const storage=new Map(saved===null?[]:[[key,JSON.stringify(saved)]]), before=JSON.stringify([...storage]);
 const selected=[], errors=[];
 const context=vm.createContext({initBookmarks:()=>({}),sections:[],bookmarks:null,fetch:async()=>({ok:true,json:async()=>book}),book:null,location:{hash:""},offlineReady:false,storageWarning:false,
  localStorage:{getItem:name=>storage.get(name)??null},initOffline:async()=>{},offlineStatus(){},downloadControls(){},
  selectChapter:async(index,options)=>selected.push({index,...options}),status:message=>errors.push(message),$:()=>({textContent:''})});
 await new vm.Script('(async()=>{'+app.match(/^const saveKey = .+$/m)[0]+startup+'})()').runInContext(context);
 assert.equal(errors.length,0);assert.equal(selected.length,1);assert.equal(selected[0].index,wantedIndex);assert.equal(selected[0].time,wantedTime);assert.equal(selected[0].play,true);
 assert.equal(JSON.stringify([...storage]),before);
 const visit=setup({checked:false,currentTime:wantedTime});visit.win.fire('pageshow');visit.flush();assert.equal(visit.checkbox.checked,true);assert.equal(visit.audio.currentTime,wantedTime);
 results.push({name,passed:true});
}
await resumeCase('Fresh storage selects title page and starts Follow',null,0,0);
await resumeCase('Existing saved-off state retains chapter/time while Follow starts on',{version:book.version,chapter:book.chapters[2].id,time:27.3,follow:false},2,27.3);
await resumeCase('Repeated reload keeps the same saved chapter/time and enables Follow',{version:book.version,chapter:book.chapters[12].id,time:137.25,follow:false},12,137.25);
await resumeCase('Stale audio revision still resets position according to existing rules',{version:'older-audio',chapter:book.chapters[2].id,time:27.3,follow:false},0,0);

test('Every reading-navigation key leaves Follow checked',()=>{
 const s=setup();document.scrollingElement.scrollHeight=20000;
 for(const key of ['PageDown','PageUp','Home','End','ArrowDown','ArrowUp',' ']){
   s.setCue(1600+s.calls.length*900);s.win.fire('keydown',{key,target:{tagName:'BODY'}});s.flush();
   assert.equal(s.checkbox.checked,true);
 }
 assert.equal(s.calls.length,7);
});
test('Native scroll and scrollbar pointer input continue following',()=>{
 const s=setup({phone:false});s.flush();s.win.fire('scroll');s.flush();
 s.win.scrollY=0;s.viewport.pageTop=0;s.win.fire('pointerdown');s.win.fire('scroll');s.flush();
 assert.equal(s.checkbox.checked,true);assert.equal(s.calls.length,2);
 s.win.fire('pointerup');s.flush();assert.equal(s.checkbox.checked,true);
});
test('Explicit off survives every gesture and can be explicitly turned back on',()=>{
 const s=setup();s.checkbox.checked=false;s.checkbox.fire('change');
 for(const event of ['wheel','touchstart','touchmove','touchend','touchcancel'])s.reading.fire(event,{deltaY:100,touches:[finger(80,140)]});
 for(const event of ['scroll','pointerdown','pointerup','orientationchange','resize'])s.win.fire(event);
 s.win.fire('keydown',{key:'PageDown'});s.viewport.fire('scroll');s.flush();
 assert.equal(s.checkbox.checked,false);assert.equal(s.calls.length,0);
 s.checkbox.checked=true;s.checkbox.fire('change');s.flush();assert.equal(s.calls.length,1);
});
test('The real app keydown handler never changes Follow',()=>{
 const block=app.match(/document\.addEventListener\('keydown',event=>\{[\s\S]*?\n\}\);/)[0];
 const checkbox={checked:true};let handler,closes=0;
 vm.runInNewContext(block,{document:{addEventListener:(name,fn)=>{handler=fn;}},$:()=>checkbox,
   bookmarks:null,closeContents:()=>closes++,showDownloads:()=>closes++});
 for(const key of ['PageDown','PageUp','Home','End','ArrowDown','ArrowUp',' '])handler({key,target:{tagName:'BODY'}});
 assert.equal(checkbox.checked,true);handler({key:'Escape',target:{tagName:'BODY'}});assert.equal(closes,2);
 checkbox.checked=false;handler({key:'PageDown',target:{tagName:'BODY'}});assert.equal(checkbox.checked,false);
});
test('No runtime module contains an automatic false checkbox assignment',()=>{
 for(const name of fs.readdirSync(web).filter(name=>name.endsWith('.js'))){
   assert.doesNotMatch(fs.readFileSync(path.join(web,name),'utf8'),/\.checked\s*=\s*false\b/,name);
 }
});

// Execute the real chapter switcher with media/DOM boundary fakes. It must leave
// checkbox state intact and carry through audio source and resumed time.
async function chapterCase(enabled){
 const s=setup({currentTime:27.3});s.checkbox.checked=enabled;s.checkbox.fire('change');s.flush();
 const elements=new Map();const get=id=>{
   if(id==='follow')return s.checkbox;
   if(!elements.has(id))elements.set(id,{setAttribute(){},classList:{remove(){}},disabled:false});
   return elements.get(id);
 };
 let metadata;Object.assign(s.audio,{duration:1000,pause(){this.paused=true;},removeAttribute(){this.src='';},
   load(){if(this.src&&metadata){const callback=metadata;metadata=null;callback();}},addEventListener(name,fn){if(name==='loadedmetadata')metadata=fn;}});
 const context=vm.createContext({bookmarks:null,navigator:{},book,current:0,epoch:0,metadataController:null,objectURL:null,loading:false,
   pendingTime:null,pendingPlay:false,validCues:[],audio:s.audio,AbortController,URL:{revokeObjectURL(){}},
   sections:book.chapters.map(()=>({hidden:false})),links:book.chapters.map(()=>({setAttribute(){},removeAttribute(){}})),
   $:get,savePosition(){},clearHighlight(){},cueNavigation:{refresh(){}},formatTime:String,status(){},closeContents(){},
   history:{replaceState(){}},window:s.win,validateCues:async()=>{},localSource:async()=> 'blob:unchanged-saved-audio',
   audioURL:chapter=>chapter.audio,startPlayback:async()=>{s.audio.paused=false;s.setCue(2200);s.schedule();}});
 const start=app.indexOf('async function selectChapter('),end=app.indexOf('\nfunction updateClock()',start);
 await new vm.Script(app.slice(start,end)+'\nselectChapter(2,{time:27.3,play:true});').runInContext(context);
 s.flush();assert.equal(s.checkbox.checked,enabled);assert.equal(s.audio.currentTime,27.3);
 assert.equal(s.audio.src,'blob:unchanged-saved-audio');assert.equal(context.current,2);
 assert.equal(elements.get('current-title').textContent,book.chapters[2].heading);
 assert.equal(context.sections.filter(section=>!section.hidden).length,1);
 results.push({name:'Real chapter switch preserves '+(enabled?'checked':'explicitly unchecked')+' state and resumed audio',passed:true});
}
await chapterCase(true);
await chapterCase(false);

const output={checked_utc:new Date().toISOString(),passed:results.length,kind:'Node regression tests with simulated DOM/viewport/storage and real startup decoder',
 native_browser_tested:false,physical_phone_tested:false,results};
fs.writeFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),'manual-only-follow-unit-validation.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({passed:results.length,native_browser_tested:false,physical_phone_tested:false}));

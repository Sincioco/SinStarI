const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(require('node:path').join(__dirname,'../asset/animated-pictures.js'), 'utf8');
class Target {
  constructor() { this.listeners = {}; this.attributes = {}; }
  addEventListener(type, handler) { (this.listeners[type] ||= []).push(handler); }
  emit(type, event = {}) { for (const handler of this.listeners[type] || []) handler(event); }
  setAttribute(key, value) { this.attributes[key] = value; }
  removeAttribute(key) { delete this.attributes[key]; if (key === 'src') this.src = ''; }
  closest(selector) { return selector === 'a' && this.isLink ? this : null; }
}
function harness() {
  let observer;
  const timers = new Map(); let timerId = 0;
  const media = new Target(); media.matches = false;
  const document = new Target(); document.hidden = false; document.activeElement = null;
  const window = new Target(); window.matchMedia = () => media;
  window.innerWidth=1200; window.innerHeight=900;
  const warnings=[]; const youtube=[];
  window.SinStarUploads={};
  window.SinStarYouTube={supported:()=>true, play:(container,id,audio,callbacks)=>{
    const player={destroyed:false,muted:!audio(),destroy(){this.destroyed=true;},mute(){this.muted=true;},unMute(){this.muted=false;}};
    youtube.push({id,audio,callbacks,player}); return Promise.resolve(player);
  }};
  const saved = {}; const subscribers=[];
  const preferences = window.SinStarMedia = {audioEnabled:false,storageAvailable:true,
    remembered:id=>saved[id],subscribe:listener=>subscribers.push(listener),
    remember(id,clip) { if(clip) saved[id]=clip; else delete saved[id]; subscribers.forEach(f=>f({kind:'choices',id})); },
    audio(value) { this.audioEnabled=value; subscribers.forEach(f=>f({kind:'audio'})); },
    external(id,clip) { if(clip) saved[id]=clip; else delete saved[id]; subscribers.forEach(f=>f({kind:'external'})); }
  };
  function host(id) {
    const value = new Target(); const classes = new Set();
    value.classList = {add:(...keys)=>keys.forEach(k=>classes.add(k)), remove:(...keys)=>keys.forEach(k=>classes.delete(k)), contains:k=>classes.has(k)};
    value.button = new Target(); value.status = new Target(); value.link = new Target();
    value.button.dataset={caption:'Example scene'};
    value.link.isLink = true; value.dataset={mediaId:id,defaultClip:id};
    value.choices=[id,id+'-v2'].map(id=>{const b=new Target();b.dataset={clip:id,src:id+'.mp4'};return b;});
    value.remember=new Target();value.remember.checked=false;value.choiceBar=new Target();value.saveStatus=new Target();
    value.youtubeButton=new Target();value.youtubeLink=new Target();value.youtubeOptions=new Target();
    value.youtubeContainer={replaceChildren(){}};
    value.stage={getBoundingClientRect:()=>({top:0,left:0,right:600,bottom:400,width:600,height:400})};
    value.video = new Target(); value.video.dataset = {src:id + '.mp4'};
    value.video.pending = []; value.video.pauseCount = 0;
    value.video.play = () => new Promise((resolve,reject) => value.video.pending.push({resolve,reject}));
    value.video.pause = () => value.video.pauseCount++;
    value.video.load = () => {};
    value.querySelector = selector => ({video:value.video,'.animation-toggle':value.button,'.animation-status':value.status,
      '.remember-clip':value.remember,'.clip-choices':value.choiceBar,'.clip-save-status':value.saveStatus,
      '.youtube-option':value.youtubeButton,'.youtube-link':value.youtubeLink,'.youtube-options':value.youtubeOptions,
      '.youtube-preview':value.youtubeContainer,'.picture-stage':value.stage}[selector]);
    value.querySelectorAll = () => value.choices;
    value.contains = target => [value,value.button,value.link].includes(target);
    value.hover = false; value.matches = () => value.hover;
    return value;
  }
  const hosts = [host('one'),host('two')];
  document.querySelectorAll = () => hosts;
  class Observer { constructor(callback) { observer = callback; } observe() {} }
  window.IntersectionObserver = Observer;
  vm.runInNewContext(source, {document,window,IntersectionObserver:Observer,
    console:{warn:(...args)=>warnings.push(args),info:(...args)=>warnings.push(args)},
    setTimeout:(callback,delay)=>{timers.set(++timerId,{callback,delay});return timerId;},
    clearTimeout:id=>timers.delete(id)});
  return {hosts,document,window,media,timers,preferences,saved,warnings,youtube,offscreen:host=>observer([{target:host,isIntersecting:false}])};
}
const tick = () => new Promise(resolve => setImmediate(resolve));
const results = [];
async function test(name, action) { const state = harness(); await action(state); results.push(name); }
(async () => {
  await test('No video download before interaction', ({hosts}) => hosts.forEach(h=>assert.equal(h.video.src,undefined)));
  await test('Hover plays muted and reveals video only after playback begins', async ({hosts:[h]}) => {
    h.emit('pointerenter',{pointerType:'mouse'}); assert.equal(h.video.src,'one.mp4'); assert.equal(h.video.muted,true);
    assert.equal(h.classList.contains('is-playing'),false); h.video.pending[0].resolve(); await tick();
    assert.equal(h.classList.contains('is-playing'),true);
  });
  await test('Moving between pictures releases the previous video', ({hosts:[a,b]}) => {
    a.emit('pointerenter',{}); b.emit('pointerenter',{}); assert.equal(a.video.src,''); assert.equal(b.video.src,'two.mp4');
  });
  await test('Late playback resolution cannot revive a departed picture', async ({hosts:[a,b]}) => {
    a.emit('pointerenter',{}); b.emit('pointerenter',{}); a.video.pending[0].resolve(); b.video.pending[0].resolve(); await tick();
    assert.equal(a.classList.contains('is-playing'),false); assert.equal(b.classList.contains('is-playing'),true);
  });
  await test('Pointer leave cancels automatic playback', ({hosts:[h]}) => {
    h.emit('pointerenter',{}); h.emit('pointerleave'); assert.equal(h.video.src,''); assert.equal(h.button.attributes['aria-pressed'],'false');
  });
  await test('Touch pointer entry does not autoplay', ({hosts:[h]}) => {
    h.emit('pointerenter',{pointerType:'touch'}); assert.equal(h.video.src,undefined);
  });
  await test('Reduced motion blocks automatic previews', ({hosts:[h],media}) => {
    media.matches=true; h.emit('pointerenter',{}); h.emit('focusin',{target:h.link}); assert.equal(h.video.src,undefined);
  });
  await test('Explicit play works with reduced motion and survives pointer leave', ({hosts:[h],media}) => {
    media.matches=true; h.button.emit('click'); h.emit('pointerleave'); assert.equal(h.video.src,'one.mp4');
    h.button.emit('click'); assert.equal(h.video.src,'');
  });
  await test('Escape stops a preview', ({hosts:[h],document}) => {
    h.button.emit('click'); document.emit('keydown',{key:'Escape'}); assert.equal(h.video.src,'');
  });
  await test('Hidden tabs stop playback', ({hosts:[h],document}) => {
    h.button.emit('click'); document.hidden=true; document.emit('visibilitychange'); assert.equal(h.video.src,'');
  });
  await test('Offscreen pictures stop playback', ({hosts:[h],offscreen}) => {
    h.button.emit('click'); offscreen(h); assert.equal(h.video.src,'');
  });
  await test('Missing videos retain the illustration, stay silent in the UI and log to the console', ({hosts:[h],warnings}) => {
    h.button.emit('click'); h.video.emit('error'); assert.equal(h.video.src,''); assert.equal(h.status.textContent,''); assert.equal(warnings.length,1);
  });
  await test('Slow failed loads time out without hiding the illustration', ({hosts:[h],timers}) => {
    h.button.emit('click'); [...timers.values()].find(t=>t.delay===12000).callback();
    assert.equal(h.video.src,''); assert.equal(h.status.textContent,'');
  });
  await test('Keyboard focus starts links but leaves buttons awaiting activation', ({hosts:[h]}) => {
    h.emit('focusin',{target:h.button}); assert.equal(h.video.src,undefined);
    h.emit('focusin',{target:h.link}); assert.equal(h.video.src,'one.mp4');
  });
  await test('Changing reduced motion stops an automatic preview', ({hosts:[h],media}) => {
    h.emit('pointerenter',{}); media.matches=true; media.emit('change'); assert.equal(h.video.src,'');
  });
  await test('Audio On enables sound and Audio Off immediately mutes the active clip', ({hosts:[h],preferences}) => {
    preferences.audio(true);h.emit('pointerenter',{});assert.equal(h.video.muted,false);
    preferences.audio(false);assert.equal(h.video.muted,true);
  });
  await test('Blocked sound falls back to visible muted playback with explicit sound action', async ({hosts:[h],preferences}) => {
    preferences.audio(true);h.emit('pointerenter',{});
    h.video.pending[0].reject(Object.assign(new Error(),{name:'NotAllowedError'}));await tick();
    assert.equal(h.video.muted,true);h.video.pending[1].resolve();await tick();
    assert.equal(h.classList.contains('is-playing'),true);assert.equal(h.button.textContent,'Play With Sound');
    assert.equal(h.button.attributes['aria-label'],'Play With Sound: Example scene');assert.equal(h.button.attributes['aria-pressed'],'false');
    h.button.emit('click');assert.equal(h.video.muted,false);h.video.pending[2].resolve();await tick();
    assert.equal(h.button.textContent,'Stop Preview');
  });
  await test('Stale blocked audio cannot revive a departed picture', async ({hosts:[a,b],preferences}) => {
    preferences.audio(true);a.emit('pointerenter',{});b.emit('pointerenter',{});
    a.video.pending[0].reject(Object.assign(new Error(),{name:'NotAllowedError'}));await tick();
    assert.equal(a.video.pending.length,1);assert.equal(a.video.src,'');
  });
  await test('Clip selection starts the alternate and keeps later hovers on that clip', ({hosts:[h]}) => {
    h.choices[1].emit('click');assert.equal(h.video.src,'one-v2.mp4');
    h.button.emit('click');h.emit('pointerenter',{});assert.equal(h.video.src,'one-v2.mp4');
    assert.equal(h.choices[1].attributes['aria-pressed'],'true');
  });
  await test('Remember saves the selected clip, follows changes, and clears without changing current playback', ({hosts:[h],saved}) => {
    h.choices[1].emit('click');assert.equal(saved.one,undefined);
    h.remember.checked=true;h.remember.emit('change');assert.equal(saved.one,'one-v2');
    h.choices[0].emit('click');assert.equal(saved.one,'one');
    h.remember.checked=false;h.remember.emit('change');assert.equal(saved.one,undefined);assert.equal(h.video.src,'one.mp4');
  });
  await test('External remembered clip changes synchronize controls and active preview', ({hosts:[h],preferences}) => {
    h.emit('pointerenter',{});preferences.external('one','one-v2');
    assert.equal(h.video.src,'one-v2.mp4');assert.equal(h.remember.checked,true);
    preferences.external('one',null);assert.equal(h.video.src,'one.mp4');assert.equal(h.remember.checked,false);
  });
  await test('Clip selection is explicit playback under reduced motion', ({hosts:[h],media}) => {
    media.matches=true;h.choices[1].emit('click');assert.equal(h.video.src,'one-v2.mp4');
  });
  await test('Storage restrictions explain the linked-view fallback', ({hosts:[h],preferences}) => {
    preferences.storageAvailable=false;h.remember.checked=true;h.remember.emit('change');
    assert.match(h.saveStatus.textContent,/follows view links/);
  });
  await test('Missing local clip starts only its matching verified YouTube video', async ({hosts:[h],window,youtube})=>{
    window.SinStarUploads.one='abcdefghijk';h.emit('pointerenter',{});h.video.emit('error');await tick();
    assert.equal(youtube.length,1);assert.equal(youtube[0].id,'abcdefghijk');assert.equal(h.status.textContent,'');
    h.video.pending[0].reject(new Error('missing'));await tick();assert.equal(youtube.length,1);
    h.emit('pointerleave');assert.equal(youtube[0].player.destroyed,true);
  });
  await test('An unavailable local file is not repeatedly requested on each hover', ({hosts:[h]})=>{
    h.emit('pointerenter',{});h.video.emit('error');h.emit('pointerenter',{});assert.equal(h.video.pending.length,1);
  });
  await test('YouTube button plays in place and global Audio Off mutes it', async ({hosts:[h],window,youtube,preferences})=>{
    window.SinStarUploads.one='abcdefghijk';preferences.audio(true);h.youtubeButton.emit('click');await tick();
    assert.equal(youtube[0].player.muted,false);assert.equal(h.classList.contains('is-youtube'),true);
    preferences.audio(false);assert.equal(youtube[0].player.muted,true);h.youtubeButton.emit('click');
    assert.equal(youtube[0].player.destroyed,true);
  });
  await test('YouTube failure removes the player and leaves no error message over the art', async ({hosts:[h],window,youtube,warnings})=>{
    window.SinStarUploads.one='abcdefghijk';h.youtubeButton.emit('click');await tick();
    youtube[0].callbacks.error(new Error('YouTube unavailable'));
    assert.equal(h.status.textContent,'');assert.equal(h.classList.contains('is-youtube'),false);assert.equal(warnings.length,1);
  });
  await test('File protocol skips unsupported YouTube embeds quietly', ({hosts:[h],window,youtube})=>{
    window.SinStarUploads.one='abcdefghijk';window.SinStarYouTube.supported=()=>false;
    h.emit('pointerenter',{});h.video.emit('error');assert.equal(youtube.length,0);assert.equal(h.status.textContent,'');
  });
  await test('Offscreen automatic YouTube fallback does not start', ({hosts:[h],window,youtube})=>{
    window.SinStarUploads.one='abcdefghijk';h.stage.getBoundingClientRect=()=>({top:850,bottom:1250,left:0,right:600,width:600,height:400});
    h.emit('pointerenter',{});h.video.emit('error');assert.equal(youtube.length,0);
  });
  await test('Changing clips updates the YouTube link to the selected take', ({hosts:[h],window})=>{
    window.SinStarUploads['one-v2']='abcdefghijk';h.choices[1].emit('click');assert.equal(h.youtubeLink.href,'https://youtu.be/abcdefghijk');
  });
  console.log(JSON.stringify({status:'Passed',checks:results.length,results},null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});

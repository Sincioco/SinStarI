import {initBookmarks} from '../bookmarks.js';
const key='sin-star-book-one-bookmarks-v2';
document.getElementById('run').onclick=async()=>{
 const before=localStorage.getItem(key),results=[];localStorage.removeItem(key);
 const check=(name,ok)=>{if(!ok)throw Error(name);results.push({name,passed:true});};
 try{
  document.getElementById('fixture').innerHTML=`<header class="topbar"></header><button id="bookmarks-toggle">Bookmarks</button><section id="ch-a"><p id="ch-a-label" data-narratable><span id="heading">Prologue</span></p><p id="ch-a-b1" data-narratable><span id="first">First spoken </span><em><span id="last">passage.</span></em></p><p id="ch-a-b2" data-narratable><span id="second">Second passage.</span></p></section><section id="ch-b"><p id="ch-b-b1" data-narratable>Another chapter.</p></section><section id="bookmarks" hidden><button id="bookmark-close">Close</button><p id="bookmark-status"></p><details id="bookmark-composer"><summary>Bookmark</summary><blockquote id="bookmark-quote"></blockquote><p id="bookmark-match"></p><textarea id="bookmark-note"></textarea><button id="bookmark-save">Save</button></details><ol id="bookmark-list"></ol></section>`;
  const get=id=>document.getElementById(id),section=get('ch-a'),sections=[section,get('ch-b')],chapters=[{id:'ch-a',heading:'Prologue — Title'},{id:'ch-b',heading:'Chapter One — Title'}];
  const cue=(id,text,nodes)=>({id,text,textHash:id,valid:true,nodes:nodes.map(get),start:4,end:8});
  const heading=cue('heading','Prologue',['heading']),first=cue('first','First spoken passage',['first','last']),second=cue('second','Second passage',['second']);
  let active=null,current=0,navigated;
  const highlight=c=>{document.querySelectorAll('.spoken').forEach(n=>n.classList.remove('spoken'));active=c;c?.nodes.forEach(n=>n.classList.add('spoken'));};
  initBookmarks({book:{chapters},sections,current:()=>current,cues:()=>[heading,first,second],spokenCue:()=>active,navigate:async item=>{navigated=item;return {section:sections[current],playing:true}},get});
  const close=()=>{if(!get('bookmarks').hidden)get('bookmark-close').click();};
  const open=()=>{get('bookmarks-toggle').dispatchEvent(new PointerEvent('pointerdown'));get('bookmarks-toggle').click();};
  const select=(node,start,end)=>{const range=document.createRange();range.setStart(node.firstChild,start);range.setEnd(node.firstChild,end);window.getSelection().removeAllRanges();window.getSelection().addRange(range);};
  highlight(first);open();check('Current yellow cue across formatted spans is captured',get('bookmark-quote').textContent==='First spoken passage.');close();
  select(get('second'),0,6);highlight(first);open();check('Valid explicit manual selection takes priority',get('bookmark-quote').textContent==='Second');close();window.getSelection().removeAllRanges();
  highlight(first);get('bookmarks-toggle').dispatchEvent(new PointerEvent('pointerdown'));highlight(second);get('bookmarks-toggle').click();check('Pointer activation freezes quote before cue advances',get('bookmark-quote').textContent==='First spoken passage.');
  get('bookmark-note').value='<img src=x onerror=alert(1)>';get('bookmark-save').click();check('Quick bookmark uses stable body block and cue',JSON.parse(localStorage.getItem(key))[0].start.blockId==='ch-a-b1'&&JSON.parse(localStorage.getItem(key))[0].cueId==='first');check('Notes render literally without HTML injection',!get('bookmark-list').querySelector('img')&&get('bookmark-list').textContent.includes('<img'));
  get('bookmark-list').querySelector('button').click();await Promise.resolve();await Promise.resolve();check('Open quick bookmark retains frozen cue',navigated.cueId==='first');close();window.getSelection().removeAllRanges();
  highlight(first);get('bookmarks-toggle').dispatchEvent(new KeyboardEvent('keydown',{key:' '}));highlight(second);get('bookmarks-toggle').click();check('Keyboard activation freezes current passage',get('bookmark-quote').textContent==='First spoken passage.');close();
  highlight(first);get('bookmarks-toggle').dispatchEvent(new KeyboardEvent('keydown',{key:' '}));highlight(second);get('bookmarks-toggle').dispatchEvent(new KeyboardEvent('keydown',{key:' ',repeat:true}));select(get('second'),0,6);document.dispatchEvent(new Event('selectionchange'));get('bookmarks-toggle').click();check('Held Space and later selection cannot replace frozen activation',get('bookmark-quote').textContent==='First spoken passage.');close();window.getSelection().removeAllRanges();
  highlight(heading);open();check('Spoken heading has a stable bookmark anchor',get('bookmark-quote').textContent==='Prologue');close();
  active=null;open();check('Paused or cleared cue does not reuse an earlier draft',get('bookmark-save').disabled&&get('bookmark-quote').textContent.includes('No passage'));close();
  highlight(first);current=1;open();check('Chapter transition rejects old chapter highlight',get('bookmark-save').disabled);close();current=0;
  highlight(first);get('first').textContent='Changed text ';open();check('Edited highlighted cue is rejected honestly',get('bookmark-save').disabled);close();get('first').textContent='First spoken ';
  get('bookmarks-toggle').click();const edit=[...get('bookmark-list').querySelectorAll('button')].find(x=>x.textContent==='Edit note');edit.click();get('bookmark-list').querySelector('textarea').value='Revised note';[...get('bookmark-list').querySelectorAll('button')].find(x=>x.textContent==='Save note').click();check('Quick bookmark note editing persists',JSON.parse(localStorage.getItem(key))[0].note==='Revised note');
  [...get('bookmark-list').querySelectorAll('button')].find(x=>x.textContent==='Delete').click();[...get('bookmark-list').querySelectorAll('button')].find(x=>x.textContent==='Delete bookmark').click();check('Quick bookmark delete removes only selected test item',JSON.parse(localStorage.getItem(key)).length===0);
  get('results').textContent=JSON.stringify({passed:results.length,results},null,2);
 }catch(error){document.getElementById('results').textContent=JSON.stringify({passed:results.length,results,error:error.stack},null,2);}
 finally{window.getSelection().removeAllRanges();if(before===null)localStorage.removeItem(key);else localStorage.setItem(key,before);document.getElementById('run').disabled=true;}
};

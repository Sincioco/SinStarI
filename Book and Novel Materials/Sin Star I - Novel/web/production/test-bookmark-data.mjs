import fs from 'node:fs';import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../bookmark-anchors.js',import.meta.url),'utf8');
const {cleanBookmarks,resolveBookmarkCue}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const results=[];const test=(name,run)=>{run();results.push({name,passed:true});};
const b={id:'a',chapterId:'ch-01',quote:'selected quote',cueId:'cue-1',cueHash:'hash',note:'<script>alert(1)</script>'};
test('Malformed old records and oversized quotes are discarded',()=>assert.equal(cleanBookmarks([null,{},b,{...b,quote:'x'.repeat(20001)}]).length,1));
test('Notes remain literal text and tolerate missing notes',()=>{assert.equal(cleanBookmarks([b])[0].note,b.note);assert.equal(cleanBookmarks([{...b,note:null}])[0].note,'');});
test('Bookmark data is bounded',()=>{assert.equal(cleanBookmarks(Array(600).fill(b)).length,500);assert.equal(cleanBookmarks([{...b,note:'x'.repeat(11000)}])[0].note.length,10000);});
test('Stable cue requires matching id, hash and currently valid text',()=>{
 const cue={id:'cue-1',textHash:'hash',valid:true,start:23};assert.equal(resolveBookmarkCue(b,[cue]).start,23);
 assert.equal(resolveBookmarkCue(b,[{...cue,textHash:'old'}]),null);assert.equal(resolveBookmarkCue(b,[{...cue,valid:false}]),null);assert.equal(resolveBookmarkCue({...b,cueId:null},[cue]),null);
});
fs.writeFileSync(new URL('./bookmark-unit-validation.json',import.meta.url),JSON.stringify({utc:new Date().toISOString(),passed:results.length,results},null,2));console.log(JSON.stringify({passed:results.length}));

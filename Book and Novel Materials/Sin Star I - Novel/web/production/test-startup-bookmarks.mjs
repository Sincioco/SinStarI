import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const web=process.argv[2]||path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const source=fs.readFileSync(path.join(web,'app.js'),'utf8');
const book=JSON.parse(fs.readFileSync(path.join(web,'book.json'),'utf8'));
const start=source.indexOf('  let index=0,time=0;');
const end=source.indexOf('  // Configure cache identity',start);
assert.ok(start>=0&&end>start,'Real startup selection block must be present');
const code=source.slice(start,end)+'\n({index,time,storageWarning})';
const saved={version:book.version,chapter:book.chapters[2].id,time:27.3};
const results=[];
function run(name,{hash='',state=null,blocked=false}={},index=0,time=0){
 const result=vm.runInNewContext(code,{book,location:{hash},storageWarning:false,saveKey:()=> 'test-key',
   localStorage:{getItem(){if(blocked)throw new Error('Storage disabled');return JSON.stringify(state);}}});
 assert.equal(result.index,index,name+' chapter');assert.equal(result.time,time,name+' time');
 if(blocked)assert.equal(result.storageWarning,true);
 results.push({name,passed:true});
}
run('Fresh open starts at title');
run('Plain reopen resumes saved chapter and time',{state:saved},2,27.3);
run('Explicit different chapter wins over saved position',{state:saved,hash:'#'+book.chapters[1].id},1,0);
run('Same chapter link retains its saved time',{state:saved,hash:'#'+book.chapters[2].id},2,27.3);
run('Fresh chapter bookmark selects requested chapter',{hash:'#'+book.chapters[1].id},1,0);
run('Unknown hash retains ordinary resume',{state:saved,hash:'#unknown'},2,27.3);
run('Stale saved version does not override a chapter bookmark',{state:{...saved,version:'obsolete'},hash:'#'+book.chapters[1].id},1,0);
run('Chapter bookmark works with blocked storage',{blocked:true,hash:'#'+book.chapters[1].id},1,0);
console.log(JSON.stringify({passed:results.length,kind:'Real startup code with storage and location boundary fakes',browser_tested:false,results},null,2));

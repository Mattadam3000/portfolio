const fs=require('fs'),path=require('path'),{JSDOM}=require('jsdom');
const repo='/Users/mattadam/Projects/portfolio';
const errors=[];
const dom=new JSDOM(fs.readFileSync(path.join(repo,'index.html'),'utf8'),{
  runScripts:'dangerously',pretendToBeVisual:true,url:'https://mattadam.art/',
  beforeParse(w){
    w.IntersectionObserver=class{constructor(cb){this.cb=cb}observe(){}unobserve(){}disconnect(){}};
    w.matchMedia=w.matchMedia||(q=>({matches:false,media:q,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}}));
    w.scrollTo=function(){};
    w.HTMLMediaElement.prototype.play=function(){return Promise.resolve()};
    w.addEventListener('error',e=>errors.push(e.message||String(e.error)));
  }
});
const {window}=dom;
window.addEventListener('load',done); setTimeout(done,3000);
let fired=false;
function done(){
  if(fired)return; fired=true;
  const d=window.document, flow=d.getElementById('flow');
  console.log('page script errors:',errors.length?errors:'none');
  if(!flow){console.error('FAIL: no #flow');process.exit(1);}
  const units=[...flow.querySelectorAll(':scope > .sortable')];
  console.log('sortable units:',units.length);

  const golden=new JSDOM(fs.readFileSync(path.join(repo,'test','golden-flow.html'),'utf8'));
  const gUnits=[...golden.window.document.querySelectorAll('#flow > .sortable')];
  console.log('golden units:  ',gUnits.length);

  const norm=el=>{
    const c=el.cloneNode(true);
    // ids/aria-labels are intentionally restored in the new build
    c.querySelectorAll('*').forEach(n=>{});
    return c.innerHTML.replace(/\s+/g,' ').trim();
  };
  let diffs=0;
  console.log('\nper-unit content comparison:');
  for(let i=0;i<Math.max(units.length,gUnits.length);i++){
    const a=units[i],b=gUnits[i];
    if(!a||!b){console.log(`  XX ${i+1}: missing`);diffs++;continue;}
    const same=norm(a)===norm(b);
    const clsSame=a.className===b.className;
    if(!same||!clsSame)diffs++;
    console.log(`  ${same&&clsSame?'OK':'XX'} ${String(i+1).padStart(2)}. ${(b.dataset.label||'').slice(0,34).padEnd(36)}${same?'':' CONTENT-DIFF'}${clsSame?'':' CLASS-DIFF'}`);
    if(!same){
      const A=norm(a),B=norm(b);
      let k=0; while(k<Math.min(A.length,B.length)&&A[k]===B[k])k++;
      console.log(`       new: ...${A.slice(Math.max(0,k-60),k+90)}`);
      console.log(`       old: ...${B.slice(Math.max(0,k-60),k+90)}`);
    }
  }
  console.log(diffs===0?'\n*** IDENTICAL — static flow reproduces the runtime flow exactly ***':`\n*** ${diffs} UNIT(S) DIFFER ***`);
  process.exit(diffs===0?0:1);
}

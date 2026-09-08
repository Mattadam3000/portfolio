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

  // content equality: collapse runs of whitespace
  const norm=el=>el.innerHTML.replace(/\s+/g,' ').trim();
  // structural equality: also drop whitespace BETWEEN block-level tags.
  // Inline runs (e.g. <span>a</span><span>b</span>) are preserved, so a stray
  // space between inline elements still fails.
  const INLINE=/^(span|a|b|i|em|strong|br|img|small|sup|sub)$/i;
  const structural=el=>{
    const c=el.cloneNode(true);
    const w=c.ownerDocument.createTreeWalker(c,4);
    const kill=[];let n;
    while(n=w.nextNode()){
      if(n.textContent.trim())continue;
      const p=n.previousElementSibling,x=n.nextElementSibling;
      const inlineNeighbour=(p&&INLINE.test(p.tagName))&&(x&&INLINE.test(x.tagName));
      if(!inlineNeighbour)kill.push(n);
    }
    kill.forEach(n=>n.remove());
    return c.innerHTML.replace(/\s+/g,' ').trim();
  };
  let diffs=0,inert=0;
  console.log('\nper-unit content comparison:');
  for(let i=0;i<Math.max(units.length,gUnits.length);i++){
    const a=units[i],b=gUnits[i];
    if(!a||!b){console.log(`  XX ${i+1}: missing`);diffs++;continue;}
    const same=norm(a)===norm(b);
    const structSame=structural(a)===structural(b);
    const clsSame=a.className===b.className;
    const real=(!structSame)||(!clsSame);
    if(real)diffs++; else if(!same)inert++;
    const tag=real?'XX':(same?'OK':'ws');
    console.log(`  ${tag} ${String(i+1).padStart(2)}. ${(b.dataset.label||'').slice(0,34).padEnd(36)}${structSame?'':' CONTENT-DIFF'}${clsSame?'':' CLASS-DIFF'}${(!same&&structSame)?' (inert whitespace only)':''}`);
    if(real){
      const A=norm(a),B=norm(b);
      let k=0; while(k<Math.min(A.length,B.length)&&A[k]===B[k])k++;
      console.log(`       new: ...${A.slice(Math.max(0,k-60),k+90)}`);
      console.log(`       old: ...${B.slice(Math.max(0,k-60),k+90)}`);
    }
  }
  console.log(diffs===0
    ?`\n*** MATCHES GOLDEN MASTER ***${inert?`  (${inert} unit(s) differ only by inert inter-block whitespace)`:''}`
    :`\n*** ${diffs} UNIT(S) DIFFER ***`);
  process.exit(diffs===0?0:1);
}

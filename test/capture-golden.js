// TRUE golden master: run the page's real JS in jsdom, snapshot #flow.
const fs=require('fs'), path=require('path'), {JSDOM}=require('jsdom');
const repo='/Users/mattadam/Projects/portfolio';
const html=fs.readFileSync(path.join(repo,'index.html'),'utf8');
const errors=[];

const dom=new JSDOM(html,{
  runScripts:'dangerously', pretendToBeVisual:true, url:'https://mattadam.art/',
  beforeParse(w){
    // Install browser APIs jsdom lacks BEFORE any page script parses.
    w.IntersectionObserver=class{constructor(cb){this.cb=cb}observe(){}unobserve(){}disconnect(){}};
    w.matchMedia=w.matchMedia||function(q){return{matches:false,media:q,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}}};
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
  const flow=window.document.getElementById('flow');
  if(!flow){console.error('FAIL: #flow not created');process.exit(1);}
  const units=[...flow.querySelectorAll(':scope > .sortable')];
  console.log('page script errors:',errors.length?errors:'none');
  console.log('sortable units:',units.length);
  fs.mkdirSync(path.join(repo,'test'),{recursive:true});
  fs.writeFileSync(path.join(repo,'test','golden-flow.html'),flow.outerHTML);
  fs.writeFileSync(path.join(repo,'test','golden-order.json'),
    JSON.stringify(units.map(u=>u.dataset.label),null,2));
  console.log('order:',units.map(u=>u.dataset.label).join(' | '));
  process.exit(0);
}

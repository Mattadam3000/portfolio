// Ongoing regression test: loads the built index.html in jsdom and asserts the
// page actually works. Unlike compare-golden.js (a one-time migration proof),
// this stays valid as content changes.
const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');
const repo = path.join(__dirname, '..');
const content = JSON.parse(fs.readFileSync(path.join(repo, 'content.json'), 'utf8'));
const errors = [], fail = [];

const dom = new JSDOM(fs.readFileSync(path.join(repo, 'index.html'), 'utf8'), {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://mattadam.art/',
  beforeParse(w) {
    w.IntersectionObserver = class { observe(){} unobserve(){} disconnect(){} };
    w.matchMedia = w.matchMedia || (q => ({ matches:false, media:q, addEventListener(){},
      removeEventListener(){}, addListener(){}, removeListener(){} }));
    w.scrollTo = () => {};
    w.HTMLMediaElement.prototype.play = () => Promise.resolve();
    w.addEventListener('error', e => errors.push(e.message || String(e.error)));
  }
});

const done = () => {
  const d = dom.window.document;
  const ck = (ok, msg) => { if (!ok) fail.push(msg); console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${msg}`); };

  ck(errors.length === 0, `no page script errors${errors.length ? ': ' + errors.join('; ') : ''}`);

  const units = [...d.querySelectorAll('#flow > .sortable')];
  ck(units.length === content.blocks.length,
     `#flow has ${units.length} blocks, content.json declares ${content.blocks.length}`);

  const ids = units.map(u => u.id);
  const want = content.blocks.map(b => b.id);
  ck(ids.join(',') === want.join(','), 'block ids match content.json order exactly');

  const empty = units.filter(u => !u.textContent.trim() && !u.querySelector('img,video'));
  ck(empty.length === 0, `no empty blocks${empty.length ? ': ' + empty.map(e => e.id) : ''}`);

  const imgs = [...d.querySelectorAll('img[src]')].filter(i => i.getAttribute('src'));
  const missing = imgs.map(i => i.getAttribute('src'))
                      .filter(s => !/^https?:/.test(s) && !fs.existsSync(path.join(repo, s.replace(/^\//, ''))));
  ck(missing.length === 0, `all ${imgs.length} image files exist${missing.length ? ': missing ' + missing : ''}`);

  const noDim = imgs.filter(i => !i.getAttribute('width') || !i.getAttribute('height'));
  ck(noDim.length === 0, `all images have width/height${noDim.length ? ': ' + noDim.map(i=>i.getAttribute('src')) : ''}`);

  const dead = [...d.querySelectorAll('.navItem[data-target]')]
    .filter(a => !units.some(u => u.dataset.label === a.getAttribute('data-target')));
  ck(dead.length === 0, `all nav links resolve${dead.length ? ': ' + dead.map(a=>a.getAttribute('data-target')) : ''}`);

  const form = d.getElementById('doorForm');
  ck(!!form && !/FORM_ID/.test(form.getAttribute('action')),
     `contact form points at a real endpoint (${form ? form.getAttribute('action') : 'MISSING'})`);

  console.log(fail.length ? `\n${fail.length} CHECK(S) FAILED` : '\nall checks passed');
  process.exit(fail.length ? 1 : 0);
};
dom.window.addEventListener('load', done); setTimeout(done, 4000);

#!/usr/bin/env python3
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'index.html')
OUT_DIR = os.path.join(ROOT, 'preview')
OUT = os.path.join(OUT_DIR, 'index.html')

PATCH = r'''
<style id="homepage-vision-preview-style">
  .homepage-work-link{position:absolute;right:20px;bottom:max(22px,env(safe-area-inset-bottom));color:var(--ink);text-decoration:none;opacity:.72;z-index:5}
  .homepage-work-link:hover{opacity:1}
  #contact{padding-top:14vh}
  #about.preview-about-source{display:none!important}
  .homepage-info-link{display:inline-block;margin-top:26px;border:0;background:transparent;color:var(--muted);font:inherit;cursor:pointer;padding:0;text-transform:uppercase;letter-spacing:.14em;font-family:var(--fm);font-size:11px;text-decoration:underline;text-underline-offset:4px;opacity:.65}
  .homepage-info-link:hover{color:var(--ink);opacity:1}
  #faq.preview-info-overlay{position:fixed;inset:0;z-index:120;display:none;max-width:none;margin:0;padding:max(72px,10vh) max(20px,8vw) 10vh;background:var(--paper);color:var(--ink);overflow-y:auto;-webkit-overflow-scrolling:touch}
  #faq.preview-info-overlay.open{display:block}
  #faq.preview-info-overlay .faq{max-width:900px;margin:0 auto}
  #faq.preview-info-overlay .preview-info-index{max-width:900px;margin:0 auto 8vh}
  .preview-about-copy{max-width:900px;margin:0 auto 9vh}
  .preview-about-copy .preview-about-label,.preview-faq-label{display:block;color:var(--muted);margin-bottom:24px}
  .preview-about-copy .lede{margin-top:0;max-width:44em}
  .preview-faq-label{max-width:900px;margin:0 auto 28px}
  .preview-info-close{position:fixed;right:20px;top:max(18px,env(safe-area-inset-top));z-index:121;border:0;background:transparent;color:var(--ink);cursor:pointer;font-family:var(--fm);font-size:11px;letter-spacing:.14em;text-transform:uppercase}
  body.preview-info-open{overflow:hidden}
  @media(max-width:760px){.homepage-work-link{right:18px;bottom:max(22px,env(safe-area-inset-bottom))}#faq.preview-info-overlay{padding-left:18px;padding-right:18px}.preview-info-close{right:18px}}
</style>
<script id="homepage-vision-preview-patch">
(function(){
  function apply(){
    const norm=s=>(s||'').replace(/\s+/g,' ').trim().toLowerCase();
    function setFactById(id,markup){
      const root=document.getElementById(id);
      if(!root) return false;
      const fact=root.querySelector('.fact');
      if(!fact) return false;
      fact.innerHTML=markup;
      return true;
    }
    function setFactByHeading(text,markup){
      const needle=norm(text);
      const h=[...document.querySelectorAll('h2,h3')].find(el=>norm(el.textContent).includes(needle));
      if(!h) return false;
      const scope=h.closest('.beat,.series-head,.sortable')||h.parentElement;
      const fact=scope&&scope.querySelector('.fact');
      if(!fact) return false;
      fact.innerHTML=markup;
      return true;
    }

    // Same accomplishments, tighter copy.
    setFactById('legends','<b>Juice WRLD.</b> 497,000 first week. The biggest posthumous debut since Tupac and Biggie. Matt Adam shot the portrait; the family chose it for the cover.');
    setFactById('wdty','<b>Future and Metro Boomin.</b> Two consecutive #1 albums, weeks apart. Matt Adam built the visual identity across both: covers, vinyl, billboards, and rollout.');
    setFactById('wsdty','The second chapter, released weeks later. Another #1. One visual world.');
    setFactById('pluto','<b>Future.</b> Matt Adam shot the rollout: billboards, posters, press, and visual assets around the music videos.');
    setFactById('weeknd','Matt Adam shot the first images of The Weeknd\'s <b>Hurry Up Tomorrow</b> era, opening the final chapter of the trilogy that began with <i>After Hours</i>.');
    setFactById('benny','Matt Adam shaped Benny Blanco\'s visual identity as he moved from producer to artist, beginning with "Eastside." He shot every visual across <b>Friends Keep Secrets 1</b> and <b>Friends Keep Secrets 2</b>, including a nine-billboard Sunset Boulevard takeover.');
    setFactById('unwrap-steal','Over 100 million views. Three documentaries, one directed by Sam Lipman-Stern of the Emmy-nominated <i>Telemarketers</i>. Matt Adam wraps original artworks like gifts, hides them in public, and releases clues. People race to find and steal them. Ownership moves through attention, speed, and the will to go get it.');
    setFactByHeading('Taschen','Matt Adam\'s photographs of Young Thug and A$AP Rocky are published in <i>Taschen\'s Ice Cold: A Hip-Hop Jewelry History</i>, credited by name.');
    setFactByHeading('Beyond the Streets','Five years photographing Dead City Punx on film in the Los Angeles underground became a documentary directed by Roger Gastman and co-executive produced by Zack de la Rocha, a book, and the exhibition <i>PUNX: The Art of Dead City & Friends</i> at Beyond the Streets, Los Angeles.');
    setFactByHeading('Nobody Came','Weeks before his first warehouse exhibition, Matt Adam ran through Hollywood in a clown costume spray-painting <b>"nobody came to my art show"</b> on a pink-wrapped canvas. Invitations arrived as pieces of concrete marked "break." On opening night, a 2,000-pound concrete monolith blocked the gate with the canvas buried inside. The crowd had to break it open to enter.');
    setFactByHeading('Paintings','Matt Adam takes familiar images, objects and symbols from popular culture and changes their context. Different mediums, same questions: what controls us, what we try to control, and who gets to decide.');

    // Warhol and Koons comparisons stay exactly as they are on the current homepage.

    const about=document.querySelector('#about .lede');
    if(about){
      about.innerHTML='<b>Matt Adam</b> is a visual architect based in Los Angeles, from Toronto, working across photography, art, creative direction, objects, and public interventions. His work is built around control: appetite, status, self-optimization, and the systems shaping what people want. He built visual worlds for Future and Metro Boomin, Juice WRLD, The Weeknd, and Benny Blanco; created <b>Unwrap &amp; Steal</b>; and has work featured by <b>NBC News</b>, <b>Taschen</b>, and <b>Beyond the Streets</b>.';
    }

    const hero=document.querySelector('.hero');
    if(hero&&!hero.querySelector('.homepage-work-link')){
      const work=document.createElement('a');
      work.href='https://mattadam.art/work';
      work.className='mono homepage-work-link';
      work.textContent='ART / WORK ↗';
      work.setAttribute('aria-label','Open Matt Adam art practice');
      hero.appendChild(work);
    }

    // About and FAQ remain available, but neither interrupts the main narrative.
    const faq=document.getElementById('faq');
    const aboutBlock=document.getElementById('about');
    const contact=document.getElementById('contact');
    if(faq&&aboutBlock&&contact){
      const aboutLede=aboutBlock.querySelector('.lede');
      aboutBlock.classList.add('preview-about-source');
      aboutBlock.setAttribute('aria-hidden','true');

      faq.classList.add('preview-info-overlay');
      document.body.appendChild(faq);

      if(!faq.querySelector('.preview-info-index')){
        const idx=document.createElement('div');
        idx.className='index mono preview-info-index';
        idx.innerHTML='<span>—</span><span>INFORMATION</span><span class="jp">情報</span>';
        faq.insertBefore(idx,faq.firstChild);
      }

      if(aboutLede&&!faq.querySelector('.preview-about-copy')){
        const aboutCopy=document.createElement('div');
        aboutCopy.className='preview-about-copy';
        const label=document.createElement('span');
        label.className='mono preview-about-label';
        label.textContent='ABOUT';
        const copy=aboutLede.cloneNode(true);
        aboutCopy.appendChild(label);
        aboutCopy.appendChild(copy);
        const faqContent=faq.querySelector('.faq');
        faq.insertBefore(aboutCopy,faqContent||null);
      }

      if(!faq.querySelector('.preview-faq-label')){
        const faqLabel=document.createElement('span');
        faqLabel.className='mono preview-faq-label';
        faqLabel.textContent='FAQ';
        const faqContent=faq.querySelector('.faq');
        faq.insertBefore(faqLabel,faqContent||null);
      }

      if(!faq.querySelector('.preview-info-close')){
        const close=document.createElement('button');
        close.type='button';
        close.className='preview-info-close';
        close.textContent='CLOSE ×';
        faq.insertBefore(close,faq.firstChild);
      }

      if(!contact.querySelector('.homepage-info-link')){
        const trigger=document.createElement('button');
        trigger.type='button';
        trigger.className='homepage-info-link';
        trigger.textContent='MORE INFO ↗';
        trigger.setAttribute('aria-label','Open About and FAQ');
        contact.appendChild(trigger);
        trigger.addEventListener('click',()=>{
          faq.classList.add('open');
          document.body.classList.add('preview-info-open');
          faq.querySelector('.preview-info-close')?.focus();
        });
      }

      faq.querySelector('.preview-info-close')?.addEventListener('click',()=>{
        faq.classList.remove('open');
        document.body.classList.remove('preview-info-open');
        contact.querySelector('.homepage-info-link')?.focus();
      });
      faq.addEventListener('click',e=>{
        if(e.target===faq){
          faq.classList.remove('open');
          document.body.classList.remove('preview-info-open');
        }
      });
      document.addEventListener('keydown',e=>{
        if(e.key==='Escape'&&faq.classList.contains('open')){
          faq.classList.remove('open');
          document.body.classList.remove('preview-info-open');
          contact.querySelector('.homepage-info-link')?.focus();
        }
      });
    }

    if(contact){
      const first=contact.querySelector('.index span');
      if(first) first.textContent='06';
    }

    // Accurate photography metadata supplied by Matt Adam, in visible grid order.
    const photoAlts=[
      'The Weeknd, Future, and Metro Boomin photographed by Matt Adam',
      'Future and Metro Boomin photographed by Matt Adam',
      'Ye, formerly Kanye West, and Kim Kardashian photographed by Matt Adam',
      'Punk show photographed by Matt Adam',
      'Street takeover photographed by Matt Adam',
      'Future in a motel photographed by Matt Adam',
      'Punk show photographed by Matt Adam',
      'Woman in a pink bath with a cross photographed by Matt Adam',
      'Benny Blanco and Selena Gomez photographed by Matt Adam'
    ];
    document.querySelectorAll('#photoGrid .gtile').forEach((tile,i)=>{
      if(!photoAlts[i]) return;
      const img=tile.querySelector('img');
      if(img) img.alt=photoAlts[i];
      tile.setAttribute('aria-label',photoAlts[i]);
    });

    // Never let the preview send a real inquiry.
    document.addEventListener('submit',function(e){
      e.preventDefault();
      alert('Preview only. Nothing was sent.');
    },true);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',apply,{once:true});
  else apply();
})();
</script>
'''

with open(SRC, encoding='utf-8') as f:
    html = f.read()

# Make root-relative assets resolve against the actual live site when the copy is
# rendered from a branch preview host.
if '<base href="https://mattadam.art/">' not in html:
    html = html.replace('<head>', '<head>\n<base href="https://mattadam.art/">', 1)

# Never index the temporary preview.
html = re.sub(r'<meta name="robots"[^>]*>', '<meta name="robots" content="noindex,nofollow">', html, count=1)
html = re.sub(r'<title>.*?</title>', '<title>PREVIEW | Matt Adam Homepage Vision</title>', html, count=1, flags=re.S)

# Do not expose live structured data on a noindex design preview.
html = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', html, flags=re.S)

if 'homepage-vision-preview-patch' not in html:
    html = html.replace('</body>', PATCH + '\n</body>', 1)

os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'wrote {OUT}')
#!/usr/bin/env python3
import html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'work.json'
OUT = ROOT / 'work' / 'index.html'


def esc(value):
    return html.escape(str(value or ''), quote=True)


def img(src, alt, eager=False):
    loading = 'eager' if eager else 'lazy'
    return f'<figure class="work-image"><img src="{esc(src)}" alt="{esc(alt)}" loading="{loading}" decoding="async"></figure>'


def gallery(images, title, cls='gallery'):
    return f'<div class="{cls}">' + ''.join(img(s, f'{title}: artwork documentation') for s in images) + '</div>'


def section(s):
    parts = [
        f'<section class="work-section" id="{esc(s["id"])}">',
        '<div class="section-index mono">',
        f'<span>{esc(s["number"])}</span><span>{esc(s["title"])}</span><span>{esc(s["label"])}</span>',
        '</div>',
        '<div class="section-copy reveal">',
        f'<p class="kicker mono">{esc(s["label"])}</p>',
        f'<h2>{esc(s["title"])}</h2>',
        f'<p class="lead">{esc(s["intro"])}</p>',
        f'<p class="body-copy">{esc(s["copy"])}</p>',
        '</div>'
    ]
    if s.get('stats'):
        parts.append('<div class="stats reveal">' + ''.join(f'<span>{esc(x)}</span>' for x in s['stats']) + '</div>')
    if s.get('projects'):
        for i, p in enumerate(s['projects']):
            parts.extend([
                f'<div class="project reveal"><div class="project-copy"><span class="mono">{i+1:02d}</span><h3>{esc(p["title"])}</h3><p>{esc(p["copy"])}</p></div>',
                gallery(p.get('images', []), p['title'], 'gallery project-gallery'),
                '</div>'
            ])
    elif s.get('images'):
        parts.append(gallery(s['images'], s['title']))
    parts.append('</section>')
    return '\n'.join(parts)


def render(data):
    hero = data['hero']
    sections = '\n'.join(section(s) for s in data['sections'])
    record = data['record']
    about = data['about']
    record_items = ''.join(f'<span>{esc(x)}</span>' for x in record['items'])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Work — Matt Adam</title>
<meta name="description" content="Paintings, objects and public interventions by Matt Adam.">
<link rel="canonical" href="https://mattadam.art/work/">
<meta property="og:title" content="Work — Matt Adam">
<meta property="og:description" content="Paintings, objects and public interventions about control.">
<meta property="og:url" content="https://mattadam.art/work/">
<style>
:root{{--paper:#f3f1eb;--ink:#0a0a0a;--line:rgba(10,10,10,.22);--pad:clamp(18px,3vw,48px);--mono:"SFMono-Regular",Consolas,"Liberation Mono",monospace}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth;background:var(--paper)}}body{{margin:0;color:var(--ink);background:var(--paper);font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}}a{{color:inherit;text-decoration:none}}.mono{{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase}}
.topbar{{position:fixed;z-index:20;top:0;left:0;right:0;display:flex;justify-content:space-between;align-items:center;padding:18px var(--pad);color:#fff;mix-blend-mode:difference}}.topbar .mark{{font-weight:700;letter-spacing:-.03em}}.topbar nav{{display:flex;gap:18px}}.topbar a:hover{{opacity:.55}}
.hero-video{{position:relative;height:100svh;min-height:620px;background:#111;overflow:hidden;color:#fff}}.hero-video video{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;filter:saturate(.92) contrast(1.04)}}.hero-video:after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.12),rgba(0,0,0,.08) 42%,rgba(0,0,0,.52))}}.hero-copy{{position:absolute;z-index:2;left:var(--pad);right:var(--pad);bottom:clamp(28px,6vh,72px);display:grid;grid-template-columns:1fr minmax(280px,760px);gap:4vw;align-items:end}}.hero-copy .eyebrow{{align-self:end}}.hero-copy h1{{font-size:clamp(36px,5.5vw,88px);line-height:.94;letter-spacing:-.055em;font-weight:500;margin:0;max-width:15ch}}.hero-copy .down{{display:block;margin-top:28px;font-size:12px}}
.work-section{{padding:clamp(70px,11vw,160px) var(--pad);border-top:1px solid var(--line)}}.section-index{{display:grid;grid-template-columns:70px 1fr 1fr;border-top:1px solid var(--ink);padding-top:10px;margin-bottom:clamp(60px,9vw,130px)}}.section-index span:last-child{{text-align:right}}.section-copy{{display:grid;grid-template-columns:minmax(120px,.55fr) 1.25fr 1fr;gap:clamp(24px,4vw,70px);align-items:start;margin-bottom:clamp(46px,7vw,100px)}}.kicker{{margin:8px 0 0}}h2{{font-size:clamp(48px,8vw,128px);line-height:.84;letter-spacing:-.065em;font-weight:500;margin:0}}.lead{{font-size:clamp(22px,2.7vw,43px);line-height:1.08;letter-spacing:-.035em;margin:0}}.body-copy{{grid-column:3;margin:24px 0 0;font-size:15px;line-height:1.5;max-width:46ch}}
.gallery{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(10px,1.5vw,24px)}}.gallery .work-image:nth-child(3n){{grid-column:1/-1}}.work-image{{margin:0;background:#ddd;overflow:hidden;min-height:24vw}}.work-image img{{display:block;width:100%;height:100%;object-fit:cover;aspect-ratio:4/5}}.gallery .work-image:nth-child(3n) img{{aspect-ratio:16/10}}#paintings .gallery{{grid-template-columns:repeat(3,minmax(0,1fr))}}#paintings .gallery .work-image{{grid-column:auto}}#paintings .gallery .work-image img{{aspect-ratio:4/5}}
@media(min-width:761px){{#skinny .gallery .work-image:nth-child(3) img{{object-position:center 42%}}}}
.stats{{display:flex;gap:clamp(22px,6vw,90px);font-size:clamp(30px,5vw,76px);letter-spacing:-.05em;margin:-30px 0 70px;border-bottom:1px solid var(--ink);padding-bottom:25px}}.project{{margin-top:clamp(80px,11vw,150px)}}.project-copy{{display:grid;grid-template-columns:70px minmax(180px,.7fr) 1fr;gap:28px;border-top:1px solid var(--ink);padding:12px 0 32px;align-items:start}}.project-copy h3{{font-size:clamp(34px,5vw,74px);line-height:.92;letter-spacing:-.05em;margin:0;font-weight:500}}.project-copy p{{font-size:18px;line-height:1.35;margin:4px 0 0;max-width:45ch}}.project-gallery{{grid-template-columns:repeat(2,minmax(0,1fr))}}.project-gallery .work-image:nth-child(3n){{grid-column:auto}}
.record{{padding:clamp(80px,11vw,150px) var(--pad);border-top:1px solid var(--ink)}}.record h2,.about h2{{font-size:clamp(42px,7vw,105px);line-height:.9;letter-spacing:-.055em;margin:0 0 60px;font-weight:500}}.record-list{{display:flex;flex-wrap:wrap;border-top:1px solid var(--ink)}}.record-list span{{width:50%;padding:15px 0;border-bottom:1px solid var(--line);font-size:clamp(21px,3vw,42px);letter-spacing:-.03em}}.record-list span:nth-child(even){{text-align:right}}
.about{{padding:clamp(80px,12vw,180px) var(--pad);background:#0b0b0b;color:#f4f2ec}}.about p{{font-size:clamp(25px,3.6vw,58px);line-height:1.06;letter-spacing:-.045em;max-width:22ch;margin:0 0 80px}}.about-footer{{display:flex;justify-content:space-between;border-top:1px solid rgba(255,255,255,.35);padding-top:15px}}.about-footer a{{text-decoration:underline;text-underline-offset:4px}}
.reveal{{opacity:0;transform:translateY(18px);transition:opacity .65s ease,transform .65s ease}}.reveal.in{{opacity:1;transform:none}}
@media(max-width:760px){{.topbar nav a:not(:last-child){{display:none}}.hero-video{{min-height:560px}}.hero-copy{{display:block}}.hero-copy .eyebrow{{display:block;margin-bottom:18px}}.hero-copy h1{{font-size:clamp(34px,10.4vw,58px);max-width:12ch}}.section-index{{grid-template-columns:42px 1fr}}.section-index span:last-child{{display:none}}.section-copy{{display:block}}.section-copy h2{{margin:12px 0 32px}}.lead{{font-size:clamp(24px,7vw,34px)}}.body-copy{{margin-top:22px}}.gallery,#paintings .gallery{{grid-template-columns:1fr}}.gallery .work-image,.gallery .work-image:nth-child(3n),#paintings .gallery .work-image{{grid-column:auto;min-height:0}}.gallery .work-image img,.gallery .work-image:nth-child(3n) img,#paintings .gallery .work-image img{{aspect-ratio:auto;height:auto}}.stats{{display:grid;gap:14px;width:100%;max-width:100%;font-size:clamp(36px,11vw,52px);line-height:.92;letter-spacing:-.06em;margin-top:0}}.stats span{{display:block;min-width:0;max-width:100%;white-space:nowrap}}.project-copy{{grid-template-columns:38px 1fr}}.project-copy p{{grid-column:2}}.project-gallery{{grid-template-columns:1fr}}.record-list span{{width:100%}}.record-list span:nth-child(even){{text-align:left}}.about-footer{{display:block}}.about-footer span,.about-footer a{{display:block;margin-top:8px}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}.reveal{{opacity:1;transform:none;transition:none}}}}
</style>
</head>
<body>
<header class="topbar"><a class="mark" href="/">MATT ADAM</a><nav class="mono"><a href="#paintings">Paintings</a><a href="#objects">Objects</a><a href="#unwrap-steal">Unwrap & Steal</a><a href="/">Full site ↗</a></nav></header>
<main>
<section class="hero-video" aria-label="Matt Adam art practice">
<video autoplay muted loop playsinline preload="metadata" poster="{esc(hero['poster'])}" aria-hidden="true"><source src="{esc(hero['video'])}" type="video/mp4"></video>
<div class="hero-copy"><span class="eyebrow mono">{esc(hero['eyebrow'])}</span><div><h1>{esc(hero['statement'])}</h1><a class="down mono" href="#skinny">WORK ↓</a></div></div>
</section>
{sections}
<section class="record"><div class="section-index mono"><span>06</span><span>{esc(record['title'])}</span><span>SELECTED</span></div><h2>{esc(record['title'])}</h2><div class="record-list">{record_items}</div></section>
<section class="about"><div class="section-index mono"><span>07</span><span>{esc(about['title'])}</span><span>LOS ANGELES</span></div><h2>{esc(about['title'])}</h2><p>{esc(about['copy'])}</p><div class="about-footer mono"><span>MATT ADAM © 2026</span><a href="{esc(about['contact'])}">CONTACT ↗</a><a href="/">MATTADAM.ART ↗</a></div></section>
</main>
<script>const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting)e.target.classList.add('in')}}),{{threshold:.08}});document.querySelectorAll('.reveal').forEach(el=>io.observe(el));</script>
</body>
</html>'''


def main():
    data = json.loads(DATA.read_text())
    out = render(data)
    if '--check' in sys.argv:
        if not OUT.exists() or OUT.read_text() != out:
            print('work/index.html is out of date; run python3 build_work.py', file=sys.stderr)
            raise SystemExit(1)
        print('work page check OK')
        return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(out)
    print(f'built {OUT.relative_to(ROOT)} ({len(out):,} bytes)')

if __name__ == '__main__': main()

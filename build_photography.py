#!/usr/bin/env python3
"""Build the photography index and project galleries from their isolated CMS file."""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'photography'

def esc(value):
    return html.escape(str(value or ''), quote=True)

def image_source(src):
    if not isinstance(src, str) or not src:
        raise ValueError('Every published photograph needs an image.')
    if src.startswith('https://') and urlparse(src).netloc:
        return src
    path = (ROOT / unquote(src).lstrip('/')).resolve()
    if not path.is_relative_to(ROOT / 'img') or not path.is_file():
        raise ValueError(f'Image not found in img/: {src}')
    return '/' + path.relative_to(ROOT).as_posix()

def render_all(data=None):
    data = data if data is not None else json.loads((ROOT / 'photography.json').read_text())
    shell = (ROOT / 'photography-template.html').read_text()
    projects = [p for p in data.get('projects', []) if p.get('published', True)]
    slugs = set()
    for p in projects:
        slug = p['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in slugs or slug == 'edit':
            raise ValueError(f'Use a unique lowercase project URL with hyphens: {slug}')
        slugs.add(slug)
        if not p.get('title') or not p.get('images'):
            raise ValueError(f'Published project {slug} needs a title and at least one image.')
    contact = data.get('contact_url') or '/#contact'
    if not ((contact.startswith('/') and not contact.startswith('//')) or contact.startswith(('https://','mailto:'))):
        raise ValueError('Contact link must be a site path, HTTPS link, or email link.')
    def slide(p, photo, number, total, cover=False):
        src = image_source(photo['image'])
        alt = photo.get('alt') or p['title']
        image = f'<img src="{esc(src)}" alt="{esc(html.unescape(alt))}" loading="{"eager" if number == 1 else "lazy"}" decoding="async" {"fetchpriority=high" if number == 1 else ""}>'
        link = '/photography/' + p['slug'] + '/'
        if cover:
            picture = f'<a class="image-stage" href="{link}" aria-label="View {esc(p["title"])}">{image}</a>'
            label = f'<a class="project-label" href="{link}"><span>{esc(p["title"])}</span><span class="description">{esc(p.get("description"))}</span></a>'
            count = f'<a class="view-link" href="{link}" aria-label="View {esc(p["title"])} gallery">View <span aria-hidden="true">↗</span></a>'
        else:
            picture = f'<div class="image-stage">{image}</div>'
            label = f'<div class="project-label"><span>{esc(p["title"])}</span><span class="description">{esc(photo.get("caption") or p.get("description"))}</span></div>'
            count = f'<span class="counter" aria-label="Image {number} of {total}">{number:02d} / {total:02d}</span>'
        return f'<section class="slide" id="{p["slug"] if cover else "image-"+str(number)}" aria-label="{esc(p["title"])}{ "" if cover else ", image "+str(number)}">{picture}<footer class="caption">{label}{count}</footer></section>'
    def page(title, description, path, slides, back):
        values = dict(TITLE=esc(title), DESCRIPTION=esc(description), CANONICAL=esc('https://mattadam.art'+path), SLIDES=slides,
                      BACK=back, CONTACT_URL=esc(contact), CONTACT_LABEL=esc(data.get('contact_label') or 'Contact'))
        result = shell
        for key,value in values.items(): result = result.replace('{{'+key+'}}',value)
        assert not re.search(r'{{\w+}}', result)
        return result
    results = {}
    covers = []
    for n,p in enumerate(projects,1):
        photo = dict(p['images'][0])
        if p.get('cover'):
            photo['image'] = p['cover']
            photo['alt'] = p.get('cover_alt') or p['title']
        covers.append(slide(p,photo,n,len(projects),True))
        gallery = ''.join(slide(p,photo,i,len(p['images'])) for i,photo in enumerate(p['images'],1))
        back = f'<a href="/photography/#{p["slug"]}">Back <span aria-hidden="true">↗</span></a>'
        results[f'{p["slug"]}/index.html'] = page(p['title']+' · Matt Adam',p.get('description') or data['description'],'/photography/'+p['slug']+'/',gallery,back)
    index_slides = ''.join(covers) or '<section class="slide empty"><p>No projects on view.</p></section>'
    results['index.html'] = page(data['title'],data['description'],'/photography/',index_slides,'')
    return results

if __name__ == '__main__':
    pages = render_all()
    stale = [p for p in OUT.glob('*/index.html') if p.parent.name != 'edit' and p.relative_to(OUT).as_posix() not in pages]
    if '--check' in sys.argv:
        if stale or any(not (OUT / p).exists() or (OUT / p).read_text() != s for p,s in pages.items()):
            raise SystemExit('Photography pages are stale. Run python3 build_photography.py')
        print(f'Verified {len(pages)} photography pages and their image references.')
    else:
        for name,content in pages.items():
            p = OUT / name
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(content)
        for p in stale:
            p.unlink()
            if not any(p.parent.iterdir()): p.parent.rmdir()
        print(f'Built {len(pages)} photography pages.')

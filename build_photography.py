#!/usr/bin/env python3
"""Build the photography index and project galleries from their isolated CMS file."""
import html
import hashlib
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
    version = hashlib.sha256((json.dumps(data, sort_keys=True) + shell).encode()).hexdigest()[:16]
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
    def collection(p, first=False):
        photos = list(p['images'])
        if p.get('cover'):
            cover = next((photo for photo in photos if photo['image'] == p['cover']), {'image':p['cover'], 'alt':p.get('cover_alt') or p['title']})
            photos = [cover] + [photo for photo in photos if photo['image'] != p['cover']]
        items = []
        for i,photo in enumerate(photos):
            src = image_source(photo['image'])
            label = f'<div class="project-label"><span>{esc(p["title"])}</span><span class="description">{esc(photo.get("caption") or p.get("description"))}</span></div>'
            items.append(f'<div class="photo-slide" role="group" aria-label="Photograph {i+1} of {len(photos)}"><img src="{esc(src)}" alt="{esc(photo.get("alt") or p["title"])}" loading="{"eager" if first and i == 0 else "lazy"}" decoding="async"><div class="caption">{label}</div></div>')
        return f'<section class="slide" id="{p["slug"]}" data-project="{p["slug"]}" aria-label="{esc(p["title"])}"><div class="collection-track" aria-label="{esc(p["title"])} photographs">{"".join(items)}</div></section>'
    slides = ''.join(collection(p, i == 0) for i,p in enumerate(projects)) or '<section class="slide empty">No photographs on view.</section>'
    values = dict(VERSION=version, TITLE=esc(data['title']), DESCRIPTION=esc(data['description']), CANONICAL='https://mattadam.art/photography/', SLIDES=slides, START='', MODE='portfolio', BACK='', CONTACT_URL=esc(contact), CONTACT_LABEL=esc(data.get('contact_label') or 'Contact'))
    result = re.sub(r'{{(\w+)}}', lambda m:values[m[1]], shell)
    results = {'index.html':result, 'version.json':json.dumps({'version':version})+'\n'}
    # Preserve old collection links while keeping browsing on the main page.
    for p in projects:
        target = '/photography/#' + p['slug']
        results[p['slug']+'/index.html'] = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="https://mattadam.art/photography/"><title>{esc(p["title"])} · Matt Adam</title></head><body><a href="{target}">View photographs</a></body></html>'
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

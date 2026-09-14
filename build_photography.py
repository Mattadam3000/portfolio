#!/usr/bin/env python3
"""Build /photography using the existing work-page design and homepage assets."""
import html
import json
import re
import sys
from pathlib import Path
import build_work

ROOT = Path(__file__).resolve().parent

def esc(value):
    return html.escape(str(value), quote=True)

def render():
    data = json.loads((ROOT / 'photography.json').read_text())
    content = json.loads((ROOT / 'content.json').read_text())
    assets = {}
    def collect(value):
        if isinstance(value, dict):
            if value.get('key') and value.get('src') and value.get('w'):
                assets[value['key']] = value
            for child in value.values(): collect(child)
        elif isinstance(value, list):
            for child in value: collect(child)
    collect(content)
    collect(data['additional_images'])
    def photograph(key, eager=False, cls=''):
        a = assets[key]
        assert (ROOT / a['src'].lstrip('/')).is_file(), a['src']
        assert a['alt'] and a['w'] > 0 and a['h'] > 0
        return f'<figure class="photo {cls}"><button class="photo-open" type="button" aria-label="Enlarge: {esc(html.unescape(a["alt"]))}"><img src="{esc(a["src"])}" alt="{esc(html.unescape(a["alt"]))}" width="{a["w"]}" height="{a["h"]}" loading="{"eager" if eager else "lazy"}" {"fetchpriority=high" if eager else ""} decoding="async"></button></figure>'
    sequence = data['sequence'] + [a['key'] for a in data['additional_images']]
    photographs = ''.join(photograph(k, i == 0, 'full' if i in [0,3,6] else '') for i,k in enumerate(sequence))
    commissions = []
    for p in data['commissions']:
        commissions.append(f'<article class="commission" id="{esc(p["id"])}"><div class="commission-copy"><h3>{esc(p["title"])}</h3><p class="release">{esc(p["subtitle"])}</p><p class="mono">{esc(p["credit"])}</p><p>{esc(p["copy"])}</p></div><div class="commission-images">'+''.join(photograph(k) for k in p['keys'])+'</div></article>')
    # Reuse the /work shell styling so the established site language stays shared.
    work = build_work.render(json.loads((ROOT / 'work.json').read_text()))
    shared_css = re.search(r'<style>(.*?)</style>', work, re.S).group(1)
    page = (ROOT / 'photography-template.html').read_text()
    for key, value in {'TITLE':esc(data['title']), 'INTRO':esc(data['intro']), 'SHARED_CSS':shared_css, 'PHOTOGRAPHS':photographs, 'COMMISSIONS':''.join(commissions)}.items():
        page = page.replace('{{'+key+'}}', value)
    assert not re.search(r'{{\w+}}', page)
    return page

if __name__ == '__main__':
    page = render()
    out = ROOT / 'photography' / 'index.html'
    if '--check' in sys.argv:
        if not out.exists() or out.read_text() != page:
            raise SystemExit('Photography page is stale. Run python3 build_photography.py')
        print('Photography page and image references verified.')
    else:
        out.parent.mkdir(exist_ok=True)
        out.write_text(page)
        print('Built photography/index.html')

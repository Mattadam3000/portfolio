#!/usr/bin/env python3
"""
Builds index.html from template.html + parts.html + content.json.

  content.json   page ORDER (blocks[]) and beat copy (beats{})
  parts.html     per-block markup, delimited by <!--PART:id-->
  template.html  page shell, with a {{FLOW}} placeholder

Usage:
  python3 build.py           write index.html
  python3 build.py --check   validate + verify index.html is up to date (no writes)

index.html is GENERATED — never edit it by hand.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)


# ---------- rendering ----------

def img_tag(im):
    a = [f'src="{im["src"]}"', f'alt="{im.get("alt","")}"', 'loading="lazy"']
    if im.get("position"): a.append(f'style="object-position:{im["position"]}"')
    if im.get("w"): a.append(f'width="{im["w"]}"')
    if im.get("h"): a.append(f'height="{im["h"]}"')
    return "<img " + " ".join(a) + ">"

def frame(im):
    at = [f'class="{im["frame"]}"']
    if im.get("key"): at.append(f'data-key="{im["key"]}"')
    if im.get("aspect"): at.append(f'style="aspect-ratio:{im["aspect"]}"')
    return (f'      <div {" ".join(at)}><div class="veil"></div>\n'
            f'        {img_tag(im)}</div>')

def media(m):
    if m["type"] == "video":
        return (f'    <div class="play r" id="{m["id"]}" aria-label="{m["aria"]}">\n'
                f'      <video src="{m["src"]}" playsinline preload="metadata" poster="{m["poster"]}"></video>\n'
                f'      <div class="poster"><div class="btn" role="button" tabindex="0"></div></div>\n'
                f'      <span class="plabel">{m["label"]}</span>\n'
                f'    </div>')
    frames = "\n".join(frame(i) for i in m["images"])
    if m["type"] == "stack":
        return f'    <div class="{m.get("class","stack r")}">\n{frames}\n    </div>'
    return frames.replace("      <div", "    <div", 1).replace("\n        ", "\n      ")

def render(bid, b):
    open_at = []
    if b.get("layout"): open_at.append(f'class="{b["layout"]}"')
    if b.get("style"): open_at.append(f'style="{b["style"]}"')
    txt = []
    if b.get("heading"):
        txt.append(f'      <{b["heading_tag"]} class="{b["heading_class"]}">{b["heading"]}</{b["heading_tag"]}>')
    if b.get("role"):
        txt.append(f'      <p class="role r">{b["role"]}</p>')
    if b.get("fact"):
        txt.append(f'      <p class="fact r">{b["fact"]}</p>')
    open_tag = f'<div {" ".join(open_at)}>' if open_at else '<div>'
    if not b.get("media"):                       # text-only block
        return open_tag + '\n' + "\n".join(txt) + '\n  </div>'
    return (f'{open_tag}\n'
            f'    <div>\n' + "\n".join(txt) + f'\n    </div>\n'
            f'{media(b["media"])}\n  </div>')


# ---------- typed block renderers ----------

def chapter(ch):
    """The vertical Japanese label + index row that opens a section."""
    if not ch: return ''
    out = []
    if ch.get('vlabel'):
        out.append(f'<span class="vlabel mono">{ch["vlabel"]}</span>')
    if ch.get('index'):
        a, b, c = (ch['index'] + ['', '', ''])[:3]
        out.append(f'<div class="index mono"><span>{a}</span><span>{b}</span>'
                   f'<span class="jp">{c}</span></div>')
    return ''.join(out)   # no inter-tag whitespace: .vlabel is absolute, .index is block


def _spans(items):
    return ''.join(f'<span>{i}</span>' for i in items)


def r_roles(b):
    return f'<div class="roles r">{_spans(b["roles"])}</div>'


def r_roster(b):
    return (chapter(b.get('chapter')) +
            f'\n  <div class="roster-names r">\n    {_spans(b["names"])}\n  </div>')


def r_pubs(b):
    return ('<div class="pubs">\n'
            f'    <span class="plbl mono">{b["label"]}</span>\n'
            f'    <div class="names">\n      {_spans(b["names"])}\n    </div>\n'
            '  </div>')


def r_text(b):
    return f'<p class="{b.get("class","stmt-head r")}">{b["html"]}</p>'


def r_about(b):
    return chapter(b.get('chapter')) + f'\n  <p class="lede r">\n    {b["lede"]}\n  </p>'


def r_faq(b):
    rows = '\n    '.join(
        f'<details><summary>{i["q"]}</summary>\n      <p>{i["a"]}</p></details>'
        for i in b['items'])
    return f'<div class="faq">\n    {rows}\n  </div>'


def r_gallery(b):
    def p(k):
        d = b.get(k)
        if not d: return ''
        st = f' style="{d["style"]}"' if d.get('style') else ''
        cls = 'standing r' if k == 'standing' else 'fact r'
        return f'<p class="{cls}"{st}>{d["html"]}</p>'
    L = b['lead']
    lead = (f'<div class="photolead r" data-key="{L["key"]}">'
            f'<img src="{L["src"]}" alt="{L["alt"]}" loading="lazy" '
            f'width="{L["w"]}" height="{L["h"]}"></div>')
    tiles = '\n    '.join(
        f'<div class="gtile fr ph has" data-key="{t["key"]}" data-i="{i}" tabindex="0" '
        f'aria-label="{t["aria"]}"><img src="{t["src"]}" alt="{t["alt"]}" loading="lazy" '
        f'width="{t["w"]}" height="{t["h"]}"></div>'
        for i, t in enumerate(b['tiles']))
    return (chapter(b.get('chapter')) + '\n\n  ' + p('standing') + '\n  ' + p('fact') +
            '\n\n  ' + lead + '\n\n  <div class="grid r" id="photoGrid">\n    ' +
            tiles + '\n  </div>')


def r_body(items, beats):
    """Ordered block body: beats, image groups, and prose, in author order."""
    out = []
    for it in items:
        if 'beat' in it:
            out.append(render(it['beat'], beats[it['beat']]))
        elif 'prose' in it:
            p = it['prose']
            out.append(f'<div class="{p["class"]}">\n'
                       f'    <h2 class="{p["heading_class"]}">{p["heading"]}</h2>\n'
                       f'    <p class="fact">{p["fact"]}</p>\n  </div>')
        elif it.get('group') == 'duo':
            st = f' style="{it["style"]}"' if it.get('style') else ''
            inner = '\n'.join(frame(i) for i in it['images'])
            out.append(f'<div class="duo"{st}>\n{inner}\n  </div>')
        elif it.get('group') == 'single':
            im = dict(it['images'][0])
            at = [f'class="{im["frame"]}"']
            if im.get('key'): at.append(f'data-key="{im["key"]}"')
            style = '; '.join(x for x in [
                f'aspect-ratio:{im["aspect"]}' if im.get('aspect') else '',
                it.get('style') or ''] if x)
            if style: at.append(f'style="{style}"')
            out.append(f'<div {" ".join(at)}><div class="veil"></div>\n'
                       f'    {img_tag(im)}</div>')
    return '\n  '.join(out)


TYPES = {'roles': r_roles, 'roster': r_roster, 'pubs': r_pubs, 'text': r_text,
         'about': r_about, 'faq': r_faq, 'gallery': r_gallery}


# ---------- flow ----------

def read_parts():
    """Parse parts.html into {id: markup}."""
    src = open(P("parts.html")).read()
    parts = {}
    for m in re.finditer(r'<!--PART:([a-z0-9-]+)-->(.*?)<!--/PART:\1-->', src, re.S):
        parts[m.group(1)] = m.group(2).strip("\n")
    return parts


def flow(blocks, parts, beats):
    """Emit <section id="flow"> with one .sortable per block, in blocks[] order."""
    out = ['<section id="flow">']
    for b in blocks:
        at = [f'class="{b["classes"]}"', f'id="{b["id"]}"', f'data-label="{b["id"]}"']
        if b.get("aria"): at.append(f'aria-label="{b["aria"]}"')
        if b.get("type"):
            body = "  " + TYPES[b["type"]](b)
        elif b.get("body"):
            body = "  " + r_body(b["body"], beats)
        else:
            body = parts[b["id"]]
        if b.get("chapter") and not b.get("type"):
            body = "  " + chapter(b["chapter"]) + "\n" + body
        body = re.sub(r'\{\{BEAT:([^}]+)\}\}',
                      lambda m: render(m.group(1), beats[m.group(1)]), body)
        out.append(f'<div {" ".join(at)}>')
        out.append(body)
        out.append('</div>')
    out.append('</section>')
    return "\n".join(out)


# ---------- validation ----------

def validate(beats):
    """Return a list of human-readable problems. Empty list == valid."""
    errs = []
    for bid, b in beats.items():
        if "layout" not in b:
            errs.append(f'{bid}: missing "layout" (use "" for a bare div)')
        m = b.get("media")
        if not m:
            if not (b.get("heading") or b.get("fact")):
                errs.append(f'{bid}: has neither media nor text')
            continue
        if m.get("type") not in ("single", "stack", "video"):
            errs.append(f'{bid}: media.type must be single|stack|video, got {m.get("type")!r}')
        if m.get("type") == "video":
            for k in ("id", "src", "poster"):
                if not m.get(k): errs.append(f'{bid}: video media missing "{k}"')
            for k in ("src", "poster"):
                if m.get(k) and not os.path.exists(P(m[k])):
                    errs.append(f'{bid}: video {k} not found on disk: {m[k]}')
        else:
            for i, im in enumerate(m.get("images", [])):
                where = f'{bid}.images[{i}]'
                if not im.get("src"):
                    errs.append(f'{where}: missing "src"'); continue
                if not os.path.exists(P(im["src"])):
                    errs.append(f'{where}: file not found on disk: {im["src"]}')
                if not im.get("alt"):
                    errs.append(f'{where}: empty alt text ({im["src"]})')
                if not (im.get("w") and im.get("h")):
                    errs.append(f'{where}: missing width/height — causes layout shift ({im["src"]})')
    return errs


# ---------- pipeline ----------

def render_page():
    content = json.load(open(P("content.json")))
    tpl = open(P("template.html")).read()
    beats = content["beats"]
    blocks = content["blocks"]
    parts = read_parts()

    errs = validate(beats)

    ids = [b["id"] for b in blocks]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errs.append(f'duplicate block ids: {sorted(dupes)}')
    typed = {b["id"] for b in blocks if b.get("type") or b.get("body")}
    for b in blocks:
        if b.get("type"):
            if b["type"] not in TYPES:
                errs.append(f'block "{b["id"]}": unknown type "{b["type"]}" '
                            f'(known: {sorted(TYPES)})')
        elif not b.get("body") and b["id"] not in parts:
            errs.append(f'block "{b["id"]}" has no "type", no "body", and no '
                        f'<!--PART:{b["id"]}--> in parts.html')
    for pid in parts:
        if pid not in ids:
            errs.append(f'parts.html has PART:{pid} but no block with that id in content.json')
        elif pid in typed:
            errs.append(f'block "{pid}" has both a "type" and a <!--PART:{pid}--> — '
                        f'remove the PART, it is dead markup')

    used = set()
    for pid, body in parts.items():
        for bid in re.findall(r'\{\{BEAT:([^}]+)\}\}', body):
            used.add(bid)
            if bid not in beats:
                errs.append(f'PART:{pid} references unknown beat "{bid}"')
    for b in blocks:
        for it in b.get("body") or []:
            if 'beat' in it:
                used.add(it['beat'])
                if it['beat'] not in beats:
                    errs.append(f'block "{b["id"]}" references unknown beat "{it["beat"]}"')
    for bid in set(beats) - used:
        errs.append(f'beat "{bid}" is defined but never placed in parts.html')

    nav_ids = re.findall(r'data-target="([^"]+)"', tpl)
    for t in nav_ids:
        if t not in ids:
            errs.append(f'nav data-target="{t}" does not match any block id')

    if errs:
        sys.exit("validation failed:\n" + "\n".join("  - " + e for e in errs))

    if "{{FLOW}}" not in tpl:
        sys.exit("ERROR: template.html has no {{FLOW}} placeholder")
    out = tpl.replace("{{FLOW}}", flow(blocks, parts, beats))
    return out, used


def main():
    check = "--check" in sys.argv
    out, used = render_page()
    path = P("index.html")

    if check:
        current = open(path).read() if os.path.exists(path) else None
        if current != out:
            sys.exit("--check FAILED: index.html is stale or hand-edited.\n"
                     "  Run: python3 build.py")
        print(f"--check OK  ({len(out):,} bytes, {len(used)} beats, content valid)")
        return

    open(path, "w").write(out)
    print(f"built index.html  ({len(out):,} bytes, {len(used)} beats)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Builds index.html from template.html + content.json.

Edit content.json to change wording, swap images, or add a new beat.
Then run:  python3 build.py
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))

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
    open_at = [f'class="{b["layout"]}"']
    if b.get("style"): open_at.append(f'style="{b["style"]}"')
    txt = []
    if b.get("heading"):
        txt.append(f'      <{b["heading_tag"]} class="{b["heading_class"]}">{b["heading"]}</{b["heading_tag"]}>')
    if b.get("role"):
        txt.append(f'      <p class="role r">{b["role"]}</p>')
    if b.get("fact"):
        txt.append(f'      <p class="fact r">{b["fact"]}</p>')
    return (f'<div {" ".join(open_at)}>\n'
            f'    <div>\n' + "\n".join(txt) + f'\n    </div>\n'
            f'{media(b["media"])}\n  </div>')

def main():
    content = json.load(open(os.path.join(ROOT, "content.json")))
    tpl = open(os.path.join(ROOT, "template.html")).read()
    beats = content["beats"]

    missing = [m for m in re.findall(r'\{\{BEAT:([^}]+)\}\}', tpl) if m not in beats]
    if missing:
        sys.exit(f"ERROR: template references unknown beats: {missing}")

    used = set()
    def sub(m):
        used.add(m.group(1))
        return render(m.group(1), beats[m.group(1)])
    out = re.sub(r'\{\{BEAT:([^}]+)\}\}', sub, tpl)

    orphan = set(beats) - used
    if orphan:
        print(f"WARNING: content.json has beats not placed in template: {sorted(orphan)}")

    open(os.path.join(ROOT, "index.html"), "w").write(out)
    print(f"built index.html  ({len(out):,} bytes, {len(used)} beats)")

if __name__ == "__main__":
    main()

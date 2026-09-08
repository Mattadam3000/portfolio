#!/usr/bin/env python3
"""
Builds index.html from template.html + content.json.

Usage:
  python3 build.py           write index.html
  python3 build.py --check   validate + verify index.html is up to date (no writes)

Edit content.json to change wording, swap images, or add a new beat.
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


# ---------- validation ----------

def validate(beats):
    """Return a list of human-readable problems. Empty list == valid."""
    errs = []
    for bid, b in beats.items():
        if not b.get("layout"):
            errs.append(f'{bid}: missing "layout"')
        m = b.get("media")
        if not m:
            errs.append(f'{bid}: missing "media"'); continue
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

    errs = validate(beats)
    if errs:
        sys.exit("content.json validation failed:\n" + "\n".join("  - " + e for e in errs))

    missing = [m for m in re.findall(r'\{\{BEAT:([^}]+)\}\}', tpl) if m not in beats]
    if missing:
        sys.exit(f"ERROR: template references unknown beats: {missing}")

    used = set()
    out = re.sub(r'\{\{BEAT:([^}]+)\}\}',
                 lambda m: (used.add(m.group(1)), render(m.group(1), beats[m.group(1)]))[1],
                 tpl)

    orphan = set(beats) - used
    if orphan:
        print(f"WARNING: content.json has beats not placed in template: {sorted(orphan)}")
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
        print(f"--check OK  ({len(out):,} bytes, {len(used)} beats, content.json valid)")
        return

    open(path, "w").write(out)
    print(f"built index.html  ({len(out):,} bytes, {len(used)} beats)")


if __name__ == "__main__":
    main()

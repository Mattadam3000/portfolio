#!/usr/bin/env python3
"""One-time source migration for the approved mattadam.art homepage V5.

This edits the CMS/build sources, never generated index.html directly.
The normal build then regenerates index.html from content.json + template.html.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content.json"
TEMPLATE = ROOT / "template.html"
BUILD = ROOT / "build.py"


def block(blocks, bid):
    return next(b for b in blocks if b["id"] == bid)


def beat(blocks, bid):
    for b in blocks:
        for item in b.get("body") or []:
            if item.get("kind") == "beat" and item.get("id") == bid:
                return item
    raise KeyError(bid)


def set_project(item, heading, fact):
    item["heading"] = heading
    item["fact"] = fact


# ---------------- CMS CONTENT ----------------
data = json.loads(CONTENT.read_text())
blocks = data["blocks"]

# V5 music copy + punctuation.
set_project(
    beat(blocks, "juice-portrait"),
    "Legends<br>Never Die",
    "<b>Juice WRLD.</b> 497,000 first week. The biggest posthumous debut since Tupac and Biggie. Matt Adam shot the portrait; the family chose it for the cover.",
)
set_project(
    beat(blocks, "wdty"),
    "We Don't<br>Trust You",
    "<b>Future and Metro Boomin.</b> Two consecutive #1 albums, weeks apart. Matt Adam built the visual identity across both: covers, vinyl, billboards, and rollout.",
)
set_project(
    beat(blocks, "wsdty"),
    "We Still<br>Don't Trust You",
    "The second chapter, released weeks later. Another #1. One visual world.",
)
pluto = beat(blocks, "pluto-billboard")
set_project(
    pluto,
    "Mixtape<br>Pluto",
    "<b>Future.</b> Matt Adam shot the rollout: billboards, posters, press, and visual assets around the music videos.",
)
# V5 deliberately removes the street-poster frame, keeping billboard + photograph.
pluto["media"]["images"] = [
    im for im in pluto["media"]["images"] if im["src"] != "/img/6e0fb6ab6d.jpg"
]
block(blocks, "pluto")["classes"] = "sortable future-chapter"

# Add the approved The Real Me chapter from CMS content, not runtime DOM patching.
if not any(b["id"] == "real-me" for b in blocks):
    real_me = {
        "id": "real-me",
        "type": "content",
        "label": "The Real Me",
        "classes": "sortable future-second",
        "aria": "Future, The Real Me",
        "body": [{
            "kind": "beat",
            "id": "real-me-times-square",
            "layout": "beat",
            "heading_tag": "h2",
            "heading_class": "big r",
            "heading": "The Real<br>Me",
            "role": "VISUAL ROLLOUT",
            "fact": "<b>Future.</b> Matt Adam shot the photography and rollout assets across the campaign: billboards in Los Angeles and Times Square, press, and visual assets around the music videos.",
            "media": {
                "type": "single",
                "images": [{
                    "src": "/img/future-the-real-me-times-square-matt-adam.webp",
                    "alt": "Future The Real Me billboard in Times Square using photography by Matt Adam",
                    "frame": "fr r realme-crop",
                    "key": "real-me-times-square",
                    "w": 225,
                    "h": 400,
                }],
            },
        }],
    }
    i = next(i for i, b in enumerate(blocks) if b["id"] == "pluto")
    blocks.insert(i + 1, real_me)

set_project(
    beat(blocks, "weeknd-green"),
    "The Weeknd",
    "Matt Adam shot the first images of The Weeknd's <b>Hurry Up Tomorrow</b> era, opening the final chapter of the trilogy that began with <i>After Hours</i>.",
)
set_project(
    beat(blocks, "benny"),
    "Benny<br>Blanco",
    "Matt Adam shaped Benny Blanco's visual identity as he moved from producer to artist, beginning with \"Eastside.\" He shot every visual across <b>Friends Keep Secrets 1</b> and <b>Friends Keep Secrets 2</b>, including a nine-billboard Sunset Boulevard takeover.",
)

# Exact approved roster presentation.
block(blocks, "roster")["names"] = [
    "Juice WRLD", "Future", "Metro Boomin", "The Weeknd", "Kanye West",
    "Travis Scott", "Playboi Carti", "Young Thug", "21 Savage", "A$AP Rocky",
    "Nav", "Benny Blanco", "Justin Bieber", "Halsey", "Selena Gomez", "BTS",
    "Gracie Abrams", "Lykke Li", "Nas", "James Blake", "Usher", "Snoop Dogg",
    "Diplo", "Marshmello", "Calvin Harris", "Shake Shack", "Spotify",
    "Grand Marnier", "Interscope Records", "Sony Music", "Atlantic Records",
    "Capitol Records",
]

block(blocks, "statement")["html"] = "Creating worlds, not campaigns."

set_project(
    beat(blocks, "unwrap-steal"),
    "Unwrap<br>&amp; Steal",
    "Over 100 million views. Three documentaries, one directed by Sam Lipman-Stern of the Emmy-nominated <i>Telemarketers</i>. Matt Adam wraps original artworks like gifts, hides them in public, and releases clues. People race to find and steal them. Ownership moves through attention, speed, and the will to go get it.",
)
set_project(
    beat(blocks, "taschen"),
    "Taschen —<br>Ice Cold",
    "Matt Adam's photographs of Young Thug and A$AP Rocky are published in <i>Taschen's Ice Cold: A Hip-Hop Jewelry History</i>, credited by name.",
)
set_project(
    beat(blocks, "dead-city-punx"),
    "Beyond the Streets —<br>Dead City Punx",
    "Five years photographing Dead City Punx on film in the Los Angeles underground became a documentary directed by Roger Gastman and co-executive produced by Zack de la Rocha, a book, and the exhibition <i>PUNX: The Art of Dead City &amp; Friends</i> at Beyond the Streets, Los Angeles.",
)

# Objects: preserve the CMS body schema while using the approved /work composition.
objects = block(blocks, "objects")
intro = objects["body"][0]
intro["heading"] = "Objects"
intro["fact"] = "Photographs of objects, made into zines and bandanas, built to look real. An empty bag of cocaine. A piece of raw meat. An Ozempic needle. Each one makes a hidden system visible: appetite, status and body control."
project_copy = {
    "party-straw": ("PARTY", "An oversized dollar bill and cocaine staged on the street. Money as appetite, status and the performance of excess."),
    "rotten-deer": ("ROTTEN", "A deer head with blood. The Rotten zine printed, wrapped and displayed like a cut of raw meat in a butcher's case."),
    "skinny-doll": ("SKINNY", "The Ozempic image moved from public intervention into printed objects, zines and bandanas."),
}
for pid, (heading, fact) in project_copy.items():
    item = beat(blocks, pid)
    item["heading"] = heading
    item["fact"] = fact

set_project(
    beat(blocks, "nbcPlay"),
    "On<br>The News",
    "<b>Andy Warhol had soup cans. Matt Adam has the Ozempic needle.</b> Warhol was interested in what America consumed. Matt Adam is interested in what people use to control themselves. The Ozempic intervention broke past the art world and onto NBC News.",
)
set_project(
    beat(blocks, "show-canvas"),
    "Nobody Came<br>To My Art Show",
    "Weeks before his first warehouse exhibition, Matt Adam ran through Hollywood in a clown costume spray-painting <b>\"nobody came to my art show\"</b> on a pink-wrapped canvas. Invitations arrived as pieces of concrete marked \"break.\" On opening night, a 2,000-pound concrete monolith blocked the gate with the canvas buried inside. The crowd had to break it open to enter.",
)
paint = beat(blocks, "paint-ozempic")
set_project(
    paint,
    "Paintings",
    "Matt Adam takes familiar images, objects and symbols from popular culture and changes their context. Different mediums, same questions: what controls us, what we try to control, and who gets to decide.",
)
# V5 paintings: lead silver cross, the two approved new Ozempic groups, then Mickey.
paintings = block(blocks, "paintings")
lead_item = paintings["body"][0]
mickey_item = next(
    it for it in paintings["body"]
    if it.get("kind") == "single" and any(im.get("src") == "/img/04b582b3ba.jpg" for im in it.get("images", []))
)
new_pair = {
    "kind": "duo",
    "style": "margin-top:6vh",
    "images": [
        {
            "src": "/img/ozempic-paintings-matt-adam.webp",
            "alt": "Four Matt Adam Ozempic cross paintings in yellow, orange, pink and blue",
            "frame": "fr r tall fit",
            "key": "ozempic-paintings-color",
            "w": 900,
            "h": 1200,
        },
        {
            "src": "/img/ozempic-cross-camo-paintings-matt-adam.webp",
            "alt": "Group of Matt Adam Ozempic cross paintings in the studio",
            "frame": "fr r tall fit",
            "key": "ozempic-paintings-studio",
            "w": 900,
            "h": 1200,
        },
    ],
}
paintings["body"] = [lead_item, new_pair, mickey_item]

# Photography metadata approved in V5.
photo_alts = [
    "The Weeknd, Future, and Metro Boomin photographed by Matt Adam",
    "Future and Metro Boomin photographed by Matt Adam",
    "Ye, formerly Kanye West, and Kim Kardashian photographed by Matt Adam",
    "Punk show photographed by Matt Adam",
    "Street takeover photographed by Matt Adam",
    "Future in a motel photographed by Matt Adam",
    "Punk show photographed by Matt Adam",
    "Woman in a pink bath with a cross photographed by Matt Adam",
    "Benny Blanco and Selena Gomez photographed by Matt Adam",
]
photo = block(blocks, "photography")
for tile, alt in zip(photo["tiles"], photo_alts):
    tile["alt"] = alt
    tile["aria"] = alt

# About/FAQ remain CMS-managed; V5 surfaces them in an overlay rendered by build.py.
block(blocks, "about")["lede"] = "<b>Matt Adam</b> is a visual architect based in Los Angeles, from Toronto, working across photography, art, creative direction, objects, and public interventions. His work is built around control: appetite, status, self-optimization, and the systems shaping what people want. He built visual worlds for Future and Metro Boomin, Juice WRLD, The Weeknd, and Benny Blanco; created <b>Unwrap &amp; Steal</b>; and has work featured by <b>NBC News</b>, <b>Taschen</b>, and <b>Beyond the Streets</b>."
faq = block(blocks, "faq")
faq["items"] = faq["items"][:3]
# Exact V5 shorter Unwrap FAQ language.
for item in faq["items"]:
    if item["q"] == "What is Unwrap &amp; Steal?":
        item["a"] = "<b>Unwrap &amp; Steal</b> is a public art project by <b>Matt Adam</b>. He wraps original artworks like gifts, hides them in public, and releases clues so people race to find and keep them."
contact = block(blocks, "contact")
contact["chapter"]["index"][0] = "06"

CONTENT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ---------------- BUILD SOURCE ----------------
build = BUILD.read_text()
if "def r_objects_v5(" not in build:
    marker = "\n\n# ---------- flow ----------\n"
    assert marker in build, "build.py flow marker changed"
    addition = r'''

def r_objects_v5(b):
    """Approved V5 /work-style Objects composition, sourced entirely from CMS body[]."""
    intro = b["body"][0]
    projects = [it for it in b["body"][1:] if it.get("kind") == "beat"]
    out = [
        '<div class="objects-work">',
        '  <div class="objects-home-title r">',
        f'    <h2 class="big r">{intro["heading"]}</h2>',
        '    <p class="role r">APPETITE / STATUS / SELF-MANAGEMENT</p>',
        f'    <p class="fact r">{intro["fact"]}</p>',
        '  </div>',
    ]
    for n, it in enumerate(projects, 1):
        media_images = (it.get("media") or {}).get("images", [])
        gallery = []
        for im in media_images:
            gallery.append(
                '      <figure class="work-image fr r"><div class="veil"></div>'
                + img_tag(im) + '</figure>'
            )
        out.extend([
            '  <div class="project r">',
            f'    <div class="project-copy"><span class="mono">{n:02d}</span>'
            f'<h3>{it["heading"]}</h3><p>{it["fact"]}</p></div>',
            '    <div class="gallery project-gallery">',
            *gallery,
            '    </div>',
            '  </div>',
        ])
    out.append('</div>')
    return '\n'.join(out)


def r_info_v5(blocks):
    """About + FAQ overlay, rendered from the same Sveltia-managed blocks."""
    about = next(b for b in blocks if b["id"] == "about")
    faq = next(b for b in blocks if b["id"] == "faq")
    rows = '\n'.join(
        f'<details><summary>{it["q"]}</summary><p>{it["a"]}</p></details>'
        for it in faq["items"]
    )
    return (f'<div class="info-overlay" id="info">\n'
            f'  <button class="info-close" id="infoClose" type="button">CLOSE ×</button>\n'
            f'  <div class="info-inner">\n'
            f'    <div class="index mono"><span>—</span><span>INFORMATION</span><span class="jp">情報</span></div>\n'
            f'    <p class="mono">ABOUT</p>\n'
            f'    <p class="lede">{about["lede"]}</p>\n'
            f'    <p class="mono info-faq-label">FAQ</p>\n{rows}\n'
            f'  </div>\n</div>')
'''
    build = build.replace(marker, addition + marker, 1)

old = '''        if t == "content":\n            body = "  " + r_body(b["body"])'''
new = '''        if t == "content":\n            body = "  " + (r_objects_v5(b) if b["id"] == "objects" else r_body(b["body"]))'''
assert old in build or new in build, "build.py content renderer changed"
build = build.replace(old, new, 1)

old = '    out = tpl.replace("{{FLOW}}", flow(blocks, parts))\n'
new = '    out = tpl.replace("{{FLOW}}", flow(blocks, parts)).replace("{{INFO}}", r_info_v5(blocks))\n'
assert old in build or new in build, "build.py template replacement changed"
build = build.replace(old, new, 1)
BUILD.write_text(build)


# ---------------- TEMPLATE SOURCE ----------------
tpl = TEMPLATE.read_text()
# Top bar should match the /work system and link home.
tpl = tpl.replace(
    '<div class="bar mono"><span>MATT ADAM</span><span>LOS ANGELES</span></div>',
    '<div class="bar mono"><a href="/" class="mark">MATT ADAM</a><span>LOS ANGELES</span></div>',
)
# V5 footer exposes CMS-rendered information without interrupting the main narrative.
tpl = tpl.replace(
    '<footer class="mono"><span>© 2026 MATT ADAM</span><span>34.05°N 118.24°W</span></footer>',
    '<footer class="mono"><span>© 2026 MATT ADAM</span><button class="info-link" id="infoOpen" type="button">ABOUT / FAQ ↗</button><span>34.05°N 118.24°W</span></footer>\n\n{{INFO}}',
)
# Add the dedicated art-practice destination to the radial menu.
shop = '  <a class="navItem" href="https://unwrapandsteal.com" target="_blank" rel="noopener" data-external="1">Shop</a>'
work = '  <a class="navItem" href="/work/" target="_blank" rel="noopener" data-external="1">Art / Work ↗</a>\n'
if 'href="/work/"' not in tpl:
    assert shop in tpl, "shop nav item changed"
    tpl = tpl.replace(shop, work + shop, 1)

V5_CSS = r'''

  /* ===================== APPROVED HOMEPAGE V5 ===================== */
  :root{
    --paper:#f3f1eb;--ink:#0a0a0a;--accent:#ea54c6;
    --muted:rgba(10,10,10,.52);--hair:rgba(10,10,10,.22);
    --pink:#ea54c6;--v5ease:cubic-bezier(.22,1,.36,1);
  }
  html{background:var(--paper)}
  body{background:var(--paper);color:var(--ink);font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-weight:400;letter-spacing:-.005em}
  .mono{font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase}
  .bar{position:fixed;z-index:100;top:0;left:0;right:0;padding:18px clamp(18px,3vw,48px);color:#fff;mix-blend-mode:difference;pointer-events:none}
  .bar .mark,.bar span{pointer-events:auto;opacity:1;color:inherit;text-decoration:none}
  .bar .mark{font-weight:700;letter-spacing:-.03em}
  .hero{min-height:100svh;padding:0 clamp(18px,3vw,48px);max-width:none}
  .hero .claim{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:clamp(48px,11.8vw,154px);line-height:.88;letter-spacing:-.067em;font-weight:500;text-transform:uppercase}
  .hero .sub{margin-top:24px;margin-left:4px}
  .hero .down{left:clamp(18px,3vw,48px)}

  #flow{display:block;position:relative;max-width:1280px;margin:0 auto;padding:0 20px clamp(100px,14vw,180px)}
  #flow .sortable{position:relative;padding:0;margin:0}
  #flow .sortable + .sortable{margin-top:clamp(110px,15vw,190px)}
  #flow .sortable.architect{padding:clamp(70px,9vw,120px) 0;margin-top:0}
  .vlabel{display:none!important}
  .index{display:grid;grid-template-columns:70px 1fr 1fr;gap:0;border-top:1px solid var(--ink);padding-top:10px;margin-bottom:clamp(60px,8vw,105px);color:var(--ink);align-items:start}
  .index .jp{text-align:right;color:rgba(10,10,10,.55);margin-left:0}

  .architect .roles{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:clamp(34px,6.1vw,72px);line-height:.98;letter-spacing:-.045em;font-weight:500;color:var(--pink)}
  .architect .roles span{display:block}
  .roster-names{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:clamp(25px,4.2vw,52px);line-height:1.02;letter-spacing:-.038em;font-weight:500;color:var(--pink)}
  .roster-names span:not(:last-child)::after{content:" · ";white-space:pre;color:inherit}
  .roster-names span{display:inline}

  h2.big{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-weight:500;letter-spacing:-.064em;line-height:.86;text-transform:none;font-size:clamp(46px,7.5vw,108px);margin:0 0 30px;color:var(--ink)}
  .role{font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:11px;line-height:1.35;letter-spacing:.08em;font-weight:400;text-transform:uppercase;color:var(--muted);margin:0 0 22px}
  .fact{font-size:clamp(16px,1.55vw,19px);line-height:1.52;font-weight:400;max-width:46ch;color:var(--ink)}
  .fact b{font-weight:600}
  .beat{display:grid;grid-template-columns:1fr 1fr;gap:clamp(34px,6vw,92px);align-items:start;margin-bottom:clamp(100px,14vw,175px)}
  .beat.flip{grid-template-columns:1fr 1fr}
  .beat.flip .fr,.beat.flip .stack,.beat.flip .play{order:-1}
  .stack{gap:clamp(12px,1.6vw,24px)}
  .fr{background:#ddd}
  .fr .veil{background:var(--ink)}
  .fr.wide{aspect-ratio:4/3}
  .fr.realme-crop{aspect-ratio:3/4}
  .fr.realme-crop img{object-fit:cover;object-position:center center}
  .duo{gap:clamp(10px,1.5vw,24px);margin-top:0;margin-bottom:clamp(80px,10vw,130px)}
  .future-second{border-top:1px solid var(--ink);padding-top:clamp(70px,9vw,110px)!important}

  .statement{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--pink);font-size:clamp(44px,9vw,116px);line-height:.9;letter-spacing:-.055em;font-weight:500;padding:clamp(100px,13vw,170px) 0!important}
  .statement .stmt-head,.stmt-head{font:inherit;letter-spacing:inherit;line-height:inherit;text-transform:none;color:inherit}

  /* Exact /work Objects composition, but every word/image comes from content.json. */
  .objects-work{margin-top:0}
  .objects-home-title{max-width:760px;margin-bottom:clamp(70px,10vw,135px)}
  .objects-home-title .big{margin-bottom:22px}
  .objects-home-title .role{margin:0 0 22px}
  .objects-home-title .fact{max-width:38em}
  .objects-work .project{margin-top:clamp(80px,11vw,150px)}
  .objects-work .project-copy{display:grid;grid-template-columns:70px minmax(180px,.7fr) 1fr;gap:28px;border-top:1px solid var(--ink);padding:12px 0 32px;align-items:start}
  .objects-work .project-copy h3{font-size:clamp(34px,5vw,74px);line-height:.92;letter-spacing:-.05em;margin:0;font-weight:500}
  .objects-work .project-copy p{font-size:18px;line-height:1.35;margin:4px 0 0;max-width:45ch}
  .objects-work .gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(10px,1.5vw,24px)}
  .objects-work .work-image{position:relative;margin:0;background:#ddd;overflow:hidden;aspect-ratio:4/5}
  .objects-work .work-image img{display:block;width:100%;height:100%;object-fit:cover}

  .seenin{padding:0!important}
  .seenin .pubs{border-top:1px solid var(--ink);padding-top:12px;margin:0}
  .seenin .pubs .plbl{color:var(--ink)}
  .seenin .pubs .names{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--pink);font-size:clamp(21px,3vw,38px);line-height:1;letter-spacing:-.03em;font-weight:500;gap:7px 18px}
  .standing{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:clamp(34px,5.2vw,66px);line-height:.92;letter-spacing:-.045em;font-weight:500;color:var(--ink);max-width:20em}
  .standing .acc{color:var(--pink)}
  .photolead{margin-top:clamp(50px,7vw,90px)}
  .grid{gap:clamp(8px,1.1vw,14px)}

  #about,#faq{display:none!important}
  #contact{position:relative;color:#f4f2ec;background:#0b0b0b;box-shadow:0 0 0 100vmax #0b0b0b;clip-path:inset(0 -100vmax);padding-top:clamp(90px,12vw,150px)!important;padding-bottom:clamp(90px,12vw,150px)!important}
  #contact .index{border-color:#f4f2ec;color:#f4f2ec}
  #contact .index .jp{color:rgba(244,242,236,.58)}
  #contact .cta-lead{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:clamp(48px,10.5vw,138px);line-height:.88;letter-spacing:-.06em;font-weight:500;text-transform:none;color:#f4f2ec}
  #contact input,#contact textarea{color:#f4f2ec;border-color:rgba(244,242,236,.34);font-size:16px}
  #contact input::placeholder,#contact textarea::placeholder{color:rgba(244,242,236,.5)}
  #contact input:focus,#contact textarea:focus{border-color:#f4f2ec}
  #contact button{background:#f4f2ec;color:#0b0b0b;font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:11px;letter-spacing:.08em;font-weight:400;padding:16px 28px}
  .ticker{background:#0b0b0b;color:#f4f2ec;border-color:rgba(244,242,236,.28);font-weight:500;letter-spacing:-.025em}
  .ticker-inner{color:#f4f2ec;font-weight:500}
  footer{background:#0b0b0b;color:rgba(244,242,236,.68);padding-top:28px;padding-bottom:32px}
  footer .info-link{border:0;background:transparent;color:inherit;font:inherit;letter-spacing:inherit;text-transform:inherit;cursor:pointer;padding:0}
  footer .info-link:hover{color:#f4f2ec}

  .info-overlay{position:fixed;inset:0;z-index:130;background:var(--paper);color:var(--ink);overflow:auto;display:none;padding:clamp(72px,10vh,120px) clamp(18px,8vw,120px)}
  .info-overlay.open{display:block}
  .info-inner{max-width:900px;margin:0 auto}
  .info-overlay .lede{font-size:clamp(22px,3vw,38px);line-height:1.12;letter-spacing:-.035em;max-width:28ch;margin:24px 0 0;color:var(--ink)}
  .info-overlay .info-faq-label{margin-top:9vh}
  .info-overlay details{border-bottom:1px solid var(--hair);padding:22px 0}
  .info-overlay summary{font-size:clamp(17px,2.4vw,24px);font-weight:500;cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:20px}
  .info-overlay summary::-webkit-details-marker{display:none}
  .info-overlay summary::after{content:"+";font-weight:400;color:var(--muted)}
  .info-overlay details[open] summary::after{content:"–"}
  .info-overlay details p{margin-top:16px;font-size:16px;line-height:1.6;color:var(--muted);max-width:46em}
  .info-close{position:fixed;top:20px;right:20px;border:0;background:transparent;color:var(--ink);font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:11px;letter-spacing:.08em;cursor:pointer}
  body.info-open{overflow:hidden}

  #navDot{color:#0a0a0a;mix-blend-mode:normal}
  .navItem{background:var(--paper);border-color:var(--ink);font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;letter-spacing:.08em}
  .ink-btn,.panel{display:none!important}
  .r{transform:translateY(18px);transition:opacity .65s var(--v5ease),transform .65s var(--v5ease)}
  .r.in{transform:none}

  @media(max-width:860px){
    #flow{padding-left:18px;padding-right:18px}
    .beat,.beat.flip{grid-template-columns:1fr;gap:26px;margin-bottom:13vh}
    .beat.flip .fr,.beat.flip .stack,.beat.flip .play{order:0}
    .objects-work .project-copy{grid-template-columns:38px 1fr}
    .objects-work .project-copy p{grid-column:2}
    .objects-work .project-gallery{grid-template-columns:1fr}
  }
'''
if "APPROVED HOMEPAGE V5" not in tpl:
    assert "</style>" in tpl
    tpl = tpl.replace("</style>", V5_CSS + "\n</style>", 1)

V5_JS = r'''
<script id="homepage-v5-info">
(function(){
  function init(){
    var info=document.getElementById('info');
    var open=document.getElementById('infoOpen');
    var close=document.getElementById('infoClose');
    if(!info||!open||!close) return;
    function set(v){info.classList.toggle('open',v);document.body.classList.toggle('info-open',v);if(v)close.focus();}
    open.addEventListener('click',function(){set(true)});
    close.addEventListener('click',function(){set(false);open.focus()});
    info.addEventListener('click',function(e){if(e.target===info)set(false)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&info.classList.contains('open'))set(false)});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
</script>
'''
if 'id="homepage-v5-info"' not in tpl:
    tpl = tpl.replace("</body>", V5_JS + "\n</body>", 1)

TEMPLATE.write_text(tpl)

print("Applied approved homepage V5 to CMS/build sources.")

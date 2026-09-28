#!/usr/bin/env python3
"""Keep the homepage Instagram route in the top-right utility area.

/work and /photography already have their approved Instagram placement in their
own builders and are intentionally left untouched here.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IG_URL = "https://www.instagram.com/mattadam___/"
home = ROOT / "index.html"
text = home.read_text()

# Remove the older homepage radial-nav Instagram item if it exists.
old_nav = f'  <a class="navItem" href="{IG_URL}" target="_blank" rel="noopener noreferrer" data-external="1">Instagram ↗</a>\n'
text = text.replace(old_nav, "")

# Replace LOS ANGELES with CONTACT + INSTAGRAM in the homepage top-right bar.
old_bar = '<div class="bar"><a href="/" class="mark">MATT ADAM</a><span class="mono">LOS ANGELES</span></div>'
new_bar = (
    '<div class="bar"><a href="/" class="mark">MATT ADAM</a>'
    '<span class="mono"><a href="#contact">CONTACT</a>&nbsp;&nbsp;'
    f'<a href="{IG_URL}" target="_blank" rel="noopener noreferrer">INSTAGRAM</a></span></div>'
)

if new_bar not in text:
    if old_bar not in text:
        raise SystemExit("Homepage top-bar marker not found")
    text = text.replace(old_bar, new_bar, 1)

# The top bar inherits its difference-mode styling; make the new text links inherit too.
style_marker = '.bar .mark,.bar span{pointer-events:auto;opacity:1;color:inherit;text-decoration:none}'
style_replacement = '.bar .mark,.bar span{pointer-events:auto;opacity:1;color:inherit;text-decoration:none}\n  .bar span a{color:inherit;text-decoration:none}'
if style_replacement not in text:
    if style_marker not in text:
        raise SystemExit("Homepage top-bar style marker not found")
    text = text.replace(style_marker, style_replacement, 1)

home.write_text(text)
print("homepage top-right updated to CONTACT + INSTAGRAM")

#!/usr/bin/env python3
"""Add the public Instagram route to every primary portfolio surface.

Generated pages are rebuilt by GitHub Actions, so this post-build step keeps the
link consistent without hand-editing generated HTML.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IG_URL = "https://www.instagram.com/mattadam___/"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Instagram patch marker not found in {path}")
    path.write_text(text.replace(old, new, 1))


# Homepage: Instagram lives inside the existing radial navigation.
home = ROOT / "index.html"
replace_once(
    home,
    '  <a class="navItem" href="/work/" target="_blank" rel="noopener" data-external="1">Art / Work ↗</a>',
    f'  <a class="navItem" href="{IG_URL}" target="_blank" rel="noopener noreferrer" data-external="1">Instagram ↗</a>\n'
    '  <a class="navItem" href="/work/" target="_blank" rel="noopener" data-external="1">Art / Work ↗</a>',
)

# Art/work page: use the existing top navigation styling.
work = ROOT / "work" / "index.html"
replace_once(
    work,
    '<a href="/">Full site ↗</a></nav></header>',
    f'<a href="{IG_URL}" target="_blank" rel="noopener noreferrer">Instagram ↗</a><a href="/">Full site ↗</a></nav></header>',
)

# Photography: use the same restrained topbar typography as the rest of the page.
photo = ROOT / "photography" / "index.html"
replace_once(
    photo,
    '</nav></header>',
    f'<a href="{IG_URL}" target="_blank" rel="noopener noreferrer">Instagram ↗</a></nav></header>',
)

print("added Instagram links to homepage, work, and photography")

# mattadam.art

Live at **https://mattadam.art** via GitHub Pages (`main` branch, root).

## Structure

```
content.json   page ORDER (blocks[]) + beat copy (beats{})
parts.html     per-block markup, delimited by <!--PART:id-->
template.html  page shell (head, styles, hero, nav, footer, scripts) + {{FLOW}}
        ↓
   build.py
        ↓
   index.html   ← GENERATED. Never edit by hand.
```

## How to edit

### Change wording
Open `content.json`, find the beat, edit `heading` / `role` / `fact`. Then:
```
python3 build.py
python3 -m http.server 4321     # preview at http://localhost:4321
git add -A && git commit -m "..." && git push
```

### Reorder the page
Move entries around in `content.json` → `blocks[]`. Array order **is** page order.

### Add a new block
1. Add markup to `parts.html` between `<!--PART:my-id-->` and `<!--/PART:my-id-->`
2. Add `{"id":"my-id","label":"...","classes":"sortable","aria":"..."}` to `blocks[]`
   at the position you want it on the page
3. Build, preview, push

### Add a link to the nav
Add `<a class="navItem" href="#" data-target="my-id">Label</a>` in `template.html`.
The build fails if `data-target` doesn't match a block id.

## Verify before pushing
```
python3 build.py --check
```
Fails if `index.html` is stale or hand-edited, a referenced image is missing from disk,
an image lacks `width`/`height`, alt text is empty, a block has no matching PART, a PART
has no block, a beat is defined but never placed, block ids collide, or a nav
`data-target` points at nothing.

## Beat fields

| Field | What it does |
|---|---|
| `layout` | `beat`, `beat flip` (image left), `beat intv-beat` (series) |
| `heading` | The headline. `<br>` for line breaks |
| `role` | Small label above the description (optional) |
| `fact` | The paragraph. `<b>` works |
| `media.type` | `single`, `stack` (2+ stacked images), `video` |
| `images[].frame` | `fr r`, `fr wide`, `fr r tall`, `fr r wide fit` |
| `images[].w` / `h` | Pixel dimensions — required, prevents layout shift |

## Contact form
Posts to Formspree (`xkjnqajj`), wired in `template.html`. If the endpoint is ever unset,
the form shows an honest "FORM OFFLINE" message rather than a false confirmation.

## test/
Regression tests that run the real page scripts in jsdom. See `test/README.md`.

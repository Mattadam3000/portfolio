# mattadam.art

Live at **https://mattadam.art** via GitHub Pages (`main` branch, root).

## How to edit

All copy lives in **`content.json`**. Layout, styles and scripts live in **`template.html`**.
`index.html` is **generated** — never edit it by hand, your changes will be overwritten.

```
content.json  ─┐
               ├─→  python3 build.py  ─→  index.html  ─→  git push  ─→  live
template.html ─┘
```

### Change wording
1. Open `content.json`, find the beat, edit `heading` / `role` / `fact`
2. `python3 build.py`
3. Preview: `python3 -m http.server 4321` → http://localhost:4321
4. `git add -A && git commit -m "..." && git push`

### Add a new project
1. Drop the image in `img/`
2. Add a beat to `content.json` (copy an existing one as a starting point)
3. Add `{{BEAT:your-id}}` where you want it in `template.html`
4. Build, preview, push

### Beat fields
| Field | What it does |
|---|---|
| `layout` | `beat`, `beat flip` (image left), `beat intv-beat` (series) |
| `heading` | The big headline. `<br>` for line breaks |
| `role` | Small label above the description (optional) |
| `fact` | The paragraph. `<b>` works |
| `media.type` | `single`, `stack` (2+ stacked images), `video` |
| `images[].frame` | `fr r`, `fr wide`, `fr r tall`, `fr r wide fit` |
| `images[].w` / `h` | Pixel dimensions — **required**, prevents layout shift |

`build.py` fails loudly if `template.html` references a beat that doesn't exist,
and warns if `content.json` has a beat you forgot to place.

## Contact form
Posts to Formspree. The endpoint is in `template.html` (`<form id="doorForm" action="...">`).
If the action still contains `FORM_ID`, the form shows an honest "FORM OFFLINE" message
rather than a false confirmation.

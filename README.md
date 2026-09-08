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
1. Open `content.json`, find the beat, edit `role` / `fact`
2. `python3 build.py`
3. Preview: `python3 -m http.server 4321` → http://localhost:4321
4. `git add -A && git commit -m "..." && git push`

### Verify before pushing
```
python3 build.py --check
```
Fails if `index.html` is stale or hand-edited, if a referenced image is missing from
disk, if an image lacks `width`/`height`, or if alt text is empty.

---

## ⚠️ Two things are currently unsafe

These are real limitations of the page as it stands today, not style advice.
Both are fixed by the planned static-flow rewrite.

### 1. Do NOT edit headlines

`template.html` contains a runtime script that rebuilds the page order on every load,
identifying each block by **the exact text of its `h2`**, then applying a hardcoded
21-entry order list.

Change a headline by even one character — a period, a curly apostrophe — and that block
**silently jumps to the top of the page**, directly under the hero. The failure is wrapped
in `try{}catch(e){}`, so there is no error. It just looks wrong.

`role`, `fact`, `alt` text and images are safe to edit. Only headlines are load-bearing.

The 13 load-bearing strings:

```
Legends Never Die.        We Don't Trust You.       We Still Don't Trust You.
Mixtape Pluto.            The Weeknd.               Benny Blanco.
On The News.              Nobody Came To My Art Show.   Paintings.
Unwrap & Steal.           Objects.                  Taschen — Ice Cold.
Beyond the Streets — Dead City Punx.
```

The three series beats (`party-straw`, `rotten-deer`, `skinny-doll`) use `h3` and are
exempt — their headings are safe to edit.

### 2. Adding a beat does NOT put it where you place it

Same cause. A new `{{BEAT:id}}` placeholder renders at the **top** of the page regardless
of where you put it in `template.html`, because its headline won't be in the order list.

Source order in `template.html` is entirely ignored for the 21 blocks between the hero
and the footer.

---

## Beat fields

| Field | What it does |
|---|---|
| `layout` | `beat`, `beat flip` (image left), `beat intv-beat` (series) |
| `heading` | The big headline. `<br>` for line breaks. **See warning above** |
| `role` | Small label above the description (optional) |
| `fact` | The paragraph. `<b>` works |
| `media.type` | `single`, `stack` (2+ stacked images), `video` |
| `images[].frame` | `fr r`, `fr wide`, `fr r tall`, `fr r wide fit` |
| `images[].w` / `h` | Pixel dimensions — required, prevents layout shift |

## Contact form
Posts to Formspree (`xkjnqajj`), wired in `template.html`. If the endpoint is ever
unset, the form shows an honest "FORM OFFLINE" message rather than a false confirmation.

## test/
`golden-flow.html` and `golden-order.json` are a snapshot of the current post-JS page
structure, captured by running the real page scripts in jsdom. They are the reference
for verifying the static-flow rewrite doesn't change the rendered page.

# Tests

Both run the real page scripts in jsdom, so they test what a browser actually
renders — not a reimplementation.

```
npm install            # once, in this directory
node ../test/smoke.js  # run from the repo root
```

## smoke.js — the ongoing test

Loads the built `index.html` and asserts the page works: no script errors, block
count and order match `content.json`, no empty blocks, every image file exists and
carries width/height, every nav link resolves, and the contact form points at a
real endpoint. Runs on every pull request.

Stays valid as content changes.

## compare-golden.js — a one-time migration proof

`golden-flow.html` / `golden-order.json` were captured from the page as it was
*before* page order became static — when a runtime script rebuilt the DOM on every
load. `compare-golden.js` proved the static build renders the identical structure.

**It is not a regression test and is not run in CI.** It compares against a frozen
snapshot, so it will report differences as soon as you legitimately edit content.
Keep it for reference; re-run it only if you want to re-verify that specific
migration.

It reports two classes of difference: real content/class changes (which fail), and
inert inter-block whitespace (which does not affect rendering — `.vlabel` is
`position:absolute` and `.index` is a block-level flex container). Whitespace
between *inline* elements still fails, since that does change rendering.

`capture-golden.js` re-snapshots the golden files. Only run it if you have
deliberately changed page structure and verified the result by eye.

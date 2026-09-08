# Regression tests

These run the real page scripts in jsdom, so they test what a browser actually renders —
not a reimplementation.

```
npm install jsdom      # once, in this directory
node capture-golden.js # re-snapshot golden-flow.html + golden-order.json
node compare-golden.js # verify current index.html matches the snapshot
```

`golden-flow.html` / `golden-order.json` were captured from the pre-static-flow page
(when page order was imposed at runtime by JS). `compare-golden.js` proves the current
static build renders the identical structure.

Re-capture the golden files ONLY when you have deliberately changed page structure and
verified the new output by eye. Otherwise they are the reference, not an output.

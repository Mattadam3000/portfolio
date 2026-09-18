// Node + Playwright. GitHub calls are mocked; no publishing or real sign-in occurs.
const fs = require("fs"),
  path = require("path"),
  assert = require("assert"),
  { spawn } = require("child_process");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname, ".."),
  live = JSON.parse(fs.readFileSync(path.join(root, "photography.json")));
const projects = live.projects.filter((p) => p.published !== false),
  project = projects.find((p) => p.images.length > 2),
  single = projects.find((p) => p.images.length === 1),
  nextProject = projects[projects.indexOf(project) + 1];
const base = "http://localhost:8765",
  pause = (p) => p.waitForTimeout(650),
  selector = (p) => `.slide[data-project="${p.slug}"]`;
const order = (p) =>
  p.cover
    ? [
        p.images.find((i) => i.image === p.cover) || { image: p.cover },
        ...p.images.filter((i) => i.image !== p.cover),
      ]
    : p.images;
async function index(view, p) {
  return view
    .locator(selector(p) + " .collection-track")
    .evaluate((t) => Math.round(t.scrollLeft / t.clientWidth));
}
async function mock(page) {
  await page.route("https://api.github.com/**", (route) => {
    assert.equal(route.request().method(), "GET");
    const p = new URL(route.request().url()).pathname;
    return route.fulfill({
      json:
        p === "/user"
          ? { id: 164549058 }
          : p.endsWith("/portfolio")
            ? { permissions: { push: true } }
            : {
                sha: "base",
                content: Buffer.from(JSON.stringify(live)).toString("base64"),
              },
    });
  });
}
(async () => {
  const server = spawn("python3", ["-m", "http.server", "8765"], {
    cwd: root,
    stdio: "ignore",
  });
  await new Promise((r) => setTimeout(r, 500));
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_EXECUTABLE_PATH || undefined,
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
    headless: true,
  });
  try {
    const page = await browser.newPage({
        viewport: { width: 1440, height: 1000 },
      }),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(base + "/photography/");
    assert.equal(
      await page.locator(".slide[data-project]").count(),
      projects.length,
    );
    assert.equal(await page.getByText("View collection").count(), 0);
    await page.locator(selector(project)).evaluate((e) => e.scrollIntoView());
    await pause(page);
    const photos = order(project);
    assert.equal(
      await page.locator(".gallery-dots button").count(),
      photos.length,
    );
    assert.equal(await index(page, project), 0);
    assert((await page.locator(".viewer-caption").boundingBox()).x > 700);
    await page.mouse.click(1100, 420);
    await pause(page);
    assert.equal(await index(page, project), 1, "click advances inline");
    await page.locator(".gallery-dots button").last().click();
    await pause(page);
    assert(
      await page.locator(".gallery-next").isDisabled(),
      "last photo ends set",
    );
    const y = await page.evaluate(() => scrollY);
    await page.keyboard.press("ArrowRight");
    await page.keyboard.press("ArrowRight");
    await pause(page);
    assert.equal(await index(page, project), photos.length - 1);
    assert.equal(
      await page.evaluate(() => scrollY),
      y,
      "no spill into next collection",
    );
    await page.keyboard.press("ArrowDown");
    await pause(page);
    assert(
      Math.abs(
        await page
          .locator(selector(nextProject))
          .evaluate((e) => e.getBoundingClientRect().top),
      ) < 2,
    );
    await page.keyboard.press("ArrowUp");
    await pause(page);
    assert.equal(
      await index(page, project),
      photos.length - 1,
      "return remembers position",
    );
    await page.locator(".gallery-dots button").first().click();
    await pause(page);
    assert(await page.locator(".gallery-prev").isDisabled());
    await page.keyboard.press("ArrowLeft");
    assert.equal(await index(page, project), 0);
    await page.waitForFunction(slug => document.querySelector(`#${slug} .collection-track`).scrollLeft < 1, project.slug);
    await page.screenshot({ path: "/tmp/inline-photography-desktop.png" });
    await page.locator(selector(single)).evaluate((e) => e.scrollIntoView());
    await pause(page);
    assert(
      await page.locator(".gallery-controls").isHidden(),
      "single photo has no controls",
    );
    assert.equal(await page.locator(selector(single) + " a").count(), 0);
    // Old bookmarked collection URLs still land on the correct main-page section.
    await page.goto(`${base}/photography/${project.slug}/`);
    await page.waitForURL("**/photography/#" + project.slug);
    await pause(page);
    assert(
      Math.abs(
        await page
          .locator(selector(project))
          .evaluate((e) => e.getBoundingClientRect().top),
      ) < 2,
    );
    // Visual editor uses exactly the same collection layout and current draft data.
    await mock(page);
    await page.goto(base + "/photography/edit/");
    await page.evaluate(async () => {
      token = "mock";
      await start();
    });
    await page.evaluate((slug) => {
      selected = slug;
      render();
    }, project.slug);
    for (let i = 0; i < 2; i++) {
      await page
        .locator(".card")
        .first()
        .getByRole("button", { name: "→", exact: true })
        .click();
      await page.locator("#preview").click();
      const f = page.frameLocator("#preview-frame");
      await pause(page);
      assert.equal(
        await f.locator(".slide[data-project]").count(),
        projects.length,
      );
      assert(
        Math.abs(
          await f
            .locator(selector(project))
            .evaluate((e) => e.getBoundingClientRect().top),
        ) < 2,
      );
      assert.equal(await f.getByText("View collection").count(), 0);
      await f.locator(".gallery-dots button").last().click();
      await pause(page);
      assert(await f.locator(".gallery-next").isDisabled());
      await f
        .locator(selector(nextProject))
        .evaluate((e) => e.scrollIntoView());
      await pause(page);
      assert.equal(
        await f
          .locator(".viewer-caption .project-label span")
          .first()
          .textContent(),
        nextProject.title,
      );
      await page.locator("#device").click();
      await page.locator("#close-preview").click();
    }
    await page.locator("#files").setInputFiles(root + project.images[0].image);
    await page.waitForFunction(() => !busy);
    await page.locator("#preview").click();
    const f = page.frameLocator("#preview-frame");
    await pause(page);
    await f.locator(".gallery-dots button").last().click();
    await pause(page);
    assert(
      await f
        .locator(selector(project) + " img")
        .last()
        .evaluate(
          (i) => i.src.startsWith("blob:") && i.complete && i.naturalWidth > 0,
        ),
    );
    await page.locator("#close-preview").click();
    // Touch gestures: horizontal at the end stays put; vertical moves to the next set.
    const mobile = await browser.newPage({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
    });
    await mobile.goto(base + "/photography/#" + project.slug);
    await pause(mobile);
    const cdp = await mobile.context().newCDPSession(mobile);
    async function swipe(x1, y1, x2, y2) {
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchStart",
        touchPoints: [{ x: x1, y: y1 }],
      });
      for (let i = 1; i <= 8; i++) {
        await cdp.send("Input.dispatchTouchEvent", {
          type: "touchMove",
          touchPoints: [
            { x: x1 + ((x2 - x1) * i) / 8, y: y1 + ((y2 - y1) * i) / 8 },
          ],
        });
        await mobile.waitForTimeout(25);
      }
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchEnd",
        touchPoints: [],
      });
      await pause(mobile);
    }
    await swipe(320, 420, 60, 420);
    assert.equal(await index(mobile, project), 1);
    await mobile.locator(".gallery-dots button").last().click();
    await pause(mobile);
    const my = await mobile.evaluate(() => scrollY);
    await swipe(320, 420, 60, 420);
    assert.equal(await index(mobile, project), photos.length - 1);
    assert(Math.abs((await mobile.evaluate(() => scrollY)) - my) < 2);
    await swipe(190, 650, 190, 180);
    assert(
      (await mobile.evaluate(() => scrollY)) > my + 200,
      "vertical swipe exits collection",
    );
    await mobile.locator(selector(project)).evaluate((e) => e.scrollIntoView());
    await pause(mobile);
    await mobile.screenshot({ path: "/tmp/inline-photography-mobile.png" });
    await mock(mobile);
    await mobile.goto(base + "/photography/edit/");
    await mobile.evaluate(async (slug) => {
      token = "mock";
      await start();
      selected = slug;
      render();
    }, project.slug);
    await mobile.locator("#preview").click();
    await pause(mobile);
    assert((await mobile.locator("#preview-frame").boundingBox()).height > 500);
    assert.equal(
      await mobile
        .frameLocator("#preview-frame")
        .locator(".collection-track")
        .count(),
      projects.length,
    );
    // Older CMS preview uses the same template and updates with changed entry data.
    // Test the preview component independently of external CMS login/UI.
    await page.goto(base + "/photography/");
    await page.evaluate(() => {
      window.h = () => null;
      window.createClass = (x) => x;
      window.CMS = {
        registerPreviewTemplate: (name, spec) => (window.previewSpec = spec),
      };
    });
    await page.addScriptTag({ url: base + "/admin/photography/preview.js" });
    await page.evaluate((data) => {
      document.body.replaceChildren();
      const frame = document.createElement("iframe");
      frame.id = "cms-test";
      frame.style.cssText = "width:100%;height:900px";
      document.body.append(frame);
      window.previewComponent = {
        ...window.previewSpec,
        frame,
        props: { entry: { getIn: () => data }, getAsset: (p) => p },
      };
      window.previewComponent.componentDidMount();
    }, live);
    const cms = page.frameLocator("#cms-test");
    await cms.locator(".collection-track").first().waitFor();
    assert.equal(
      await cms.locator(".collection-track").count(),
      projects.length,
    );
    assert.equal(await cms.getByText("View collection").count(), 0);
    await page.evaluate(() => {
      window.previewComponent.componentDidUpdate();
    });
    await cms.locator(".collection-track").first().waitFor();
    assert.deepEqual(errors, []);
    console.log(
      "PASS: inline sets, hard horizontal ends, vertical navigation, touch gestures, single photos, cover ordering, both backend previews, uploads and legacy links.",
    );
  } finally {
    await browser.close();
    server.kill();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

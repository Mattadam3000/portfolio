// Run with Node and Playwright installed. No real login or publishing: GitHub is mocked.
// Optional PLAYWRIGHT_MODULE and CHROMIUM_EXECUTABLE_PATH override local browser setup.
const fs = require("fs"),
  assert = require("assert"),
  { spawn, execFileSync } = require("child_process");
(async () => {
  const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
  const root = require("path").resolve(__dirname, ".."),
    live = JSON.parse(fs.readFileSync(root + "/photography.json"));
  const project = live.projects.find(
    (p) => p.images.length > 2 && p.published !== false,
  );
  const server = spawn("python3", ["-m", "http.server", "8765"], {
    cwd: root,
    stdio: "ignore",
  });
  await new Promise((r) => setTimeout(r, 600));
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_EXECUTABLE_PATH || undefined,
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
    headless: true,
  });
  try {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
    });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.route("https://api.github.com/**", async (route) => {
      const path = new URL(route.request().url()).pathname;
      const body =
        path === "/user"
          ? { id: 164549058 }
          : path.endsWith("/portfolio")
            ? { permissions: { push: true } }
            : {
                sha: "base",
                content: Buffer.from(JSON.stringify(live)).toString("base64"),
              };
      assert.equal(route.request().method(), "GET");
      await route.fulfill({ json: body });
    });
    await page.goto("http://localhost:8765/photography/edit/");
    await page.evaluate(async () => {
      token = "mock";
      await start();
    });
    // Reopen previews after scrolling/reordering repeatedly, on both device widths.
    for (let i = 0; i < 4; i++) {
      await page
        .locator(".card")
        .first()
        .getByRole("button", { name: "→", exact: true })
        .click();
      const title = await page.locator(".card input").first().inputValue();
      await page.locator(".card").last().scrollIntoViewIfNeeded();
      await page.locator("#preview").click();
      let frame = page.frameLocator("#preview-frame");
      await frame.locator(".slide").first().waitFor();
      assert.equal(
        await frame.locator(".project-label span").first().textContent(),
        title,
      );
      assert(
        (await page.locator("#preview-frame").boundingBox()).height > 500,
        "preview viewport height",
      );
      assert(
        await frame
          .locator(".slide img")
          .first()
          .evaluate((e) => e.getBoundingClientRect().height > 50),
        "preview photo has visible area",
      );
      assert(
        await frame
          .locator(".slide")
          .first()
          .evaluate((e) => Math.abs(e.getBoundingClientRect().top) < 2),
      );
      await frame
        .locator(".slide")
        .last()
        .evaluate((e) => e.scrollIntoView());
      if (i % 2 === 0) await page.locator("#device").click();
      await page.locator("#close-preview").click();
    }
    // Gallery opens inside draft preview and uses horizontal navigation.
    await page.evaluate((slug) => {
      selected = slug;
      render();
    }, project.slug);
    await page.locator("#preview").click();
    let frame = page.frameLocator("#preview-frame");
    await frame.locator(".gallery-dots button").first().waitFor();
    assert.equal(
      await frame.locator(".gallery-dots button").count(),
      project.images.length,
    );
    await frame.locator(".gallery-next").click();
    await page.waitForTimeout(700);
    assert.equal(
      await frame
        .locator(".gallery-dots button")
        .nth(1)
        .getAttribute("aria-current"),
      "true",
    );
    await frame.locator(".gallery-prev").click();
    await page.waitForTimeout(700);
    assert.equal(
      await frame
        .locator(".gallery-dots button")
        .first()
        .getAttribute("aria-current"),
      "true",
    );
    await page.locator("#device").click();
    await page.waitForTimeout(100);
    assert(
      await frame
        .locator("body")
        .evaluate((e) => e.scrollHeight <= innerHeight + 1),
    );
    await page.locator("#close-preview").click();
    await page
      .locator(".card")
      .first()
      .getByRole("button", { name: "→", exact: true })
      .click();
    const source = await page.locator(".card img").first().getAttribute("src");
    await page.locator("#preview").click();
    frame = page.frameLocator("#preview-frame");
    await frame.locator(".slide img").first().waitFor();
    assert(
      (await frame.locator(".slide img").first().getAttribute("src")).endsWith(
        source,
      ),
    );
    await frame.getByText("Back ↗", { exact: true }).click();
    await page.waitForTimeout(200);
    assert(
      await frame
        .locator("html")
        .evaluate((e) => e.classList.contains("portfolio")),
    );
    await frame.locator(".image-stage").first().click();
    await page.waitForTimeout(200);
    assert(
      await frame
        .locator("html")
        .evaluate((e) => e.classList.contains("gallery")),
    );
    await page.locator("#close-preview").click();
    // New upload must work in consecutive previews without signing in again.
    await page.locator("#files").setInputFiles(root + project.images[0].image);
    await page.waitForFunction(() => !busy);
    for (let i = 0; i < 2; i++) {
      await page.locator("#preview").click();
      frame = page.frameLocator("#preview-frame");
      await frame.locator(".slide img").last().waitFor();
      await page.waitForTimeout(250);
      assert(
        await frame
          .locator(".slide img")
          .last()
          .evaluate((e) => e.complete && e.naturalWidth > 0),
      );
      await page.locator("#close-preview").click();
    }
    await page.goto("http://localhost:8765/photography/" + project.slug + "/");
    assert(
      await page
        .locator("#projects")
        .evaluate(
          (e) =>
            e.scrollWidth > e.clientWidth &&
            e.scrollHeight <= e.clientHeight + 1,
        ),
    );
    await page.locator(".gallery-next").click();
    await page.waitForTimeout(700);
    assert.equal(
      await page
        .locator(".gallery-dots button")
        .nth(1)
        .getAttribute("aria-current"),
      "true",
    );
    for (let i = 2; i < project.images.length; i++) {
      await page.locator(".gallery-next").click();
      await page.waitForTimeout(800);
      assert.equal(
        await page
          .locator(".gallery-dots button")
          .nth(i)
          .getAttribute("aria-current"),
        "true",
        "desktop image " + i,
      );
      assert(
        await page
          .locator(".slide img")
          .nth(i)
          .evaluate((e) => e.naturalWidth > 0),
        "photo loaded " + i,
      );
    }
    await page.screenshot({ path: "/tmp/gallery-desktop.png" });
    const mobile = await browser.newPage({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
    });
    await mobile.goto(
      "http://localhost:8765/photography/" + project.slug + "/",
    );
    await mobile.locator(".gallery-dots button").nth(1).click();
    await mobile.waitForTimeout(700);
    assert.equal(
      await mobile
        .locator(".gallery-dots button")
        .nth(1)
        .getAttribute("aria-current"),
      "true",
    );
    assert(
      await mobile
        .locator("body")
        .evaluate((e) => e.scrollHeight <= innerHeight + 1),
    );
    await mobile.screenshot({ path: "/tmp/gallery-mobile.png" });
    const cdp = await mobile.context().newCDPSession(mobile);
    await cdp.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [{ x: 320, y: 420 }],
    });
    for (let x = 300; x >= 60; x -= 30) {
      await cdp.send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [{ x, y: 420 }],
      });
      await mobile.waitForTimeout(25);
    }
    await cdp.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    await mobile.waitForTimeout(700);
    assert.equal(
      await mobile
        .locator(".gallery-dots button")
        .nth(2)
        .getAttribute("aria-current"),
      "true",
      "native touch swipe",
    ); // Rapid navigation must not keep snapping back to image two.
    await page.goto("http://localhost:8765/photography/" + project.slug + "/");
    for (let i = 1; i < project.images.length; i++) {
      await page.locator(".gallery-next").click();
      await page.waitForTimeout(40);
    }
    await page.waitForTimeout(800);
    assert.equal(
      await page
        .locator(".gallery-dots button")
        .last()
        .getAttribute("aria-current"),
      "true",
      "rapid next reaches last image",
    );
    // Test the editor preview inside a touch/mobile browser context too.
    await mobile.route("https://api.github.com/**", async (route) => {
      const path = new URL(route.request().url()).pathname;
      await route.fulfill({
        json:
          path === "/user"
            ? { id: 164549058 }
            : path.endsWith("/portfolio")
              ? { permissions: { push: true } }
              : {
                  sha: "base",
                  content: Buffer.from(JSON.stringify(live)).toString("base64"),
                },
      });
    });
    await mobile.goto("http://localhost:8765/photography/edit/");
    await mobile.evaluate(async (slug) => {
      token = "mock";
      await start();
      selected = slug;
      render();
    }, project.slug);
    for (let i = 0; i < 3; i++) {
      await mobile
        .locator(".card")
        .first()
        .getByRole("button", { name: "→", exact: true })
        .click();
      await mobile.locator("#preview").click();
      const mf = mobile.frameLocator("#preview-frame");
      await mf.locator(".slide img").first().waitFor();
      assert(
        (await mobile.locator("#preview-frame").boundingBox()).height > 500,
      );
      assert(
        await mf
          .locator(".slide img")
          .first()
          .evaluate((e) => e.getBoundingClientRect().height > 100),
      );
      await mf.locator(".gallery-dots button").last().click();
      await mobile.waitForTimeout(700);
      assert.equal(
        await mf
          .locator(".gallery-dots button")
          .last()
          .getAttribute("aria-current"),
        "true",
      );
      await mobile.locator("#close-preview").click();
    }
    // A changed build marker should refresh a cached page without a hard reload.
    await page.route("**/photography/version.json?*", (route) =>
      route.fulfill({ json: { version: "abcdef0123456789" } }),
    );
    const refreshed = page.waitForRequest(request => request.isNavigationRequest() && request.url().includes('v=abcdef0123456789'));
    await page.goto("http://localhost:8765/photography/" + project.slug + "/");
    await refreshed;
    await page.waitForLoadState('load');
    await page.waitForFunction(() => !new URL(location.href).searchParams.has('v'));
    assert.equal(new URL(page.url()).searchParams.has('v'), false);
    await page.goto("http://localhost:8765/photography/?v=abcdef0123456789#pink-bath");
    await page.waitForFunction(() => !new URL(location.href).searchParams.has('v'));
    assert.equal(new URL(page.url()).hash, '#pink-bath');
    assert.deepEqual(errors, []);
    console.log(
      "PASS: repeated previews, reorder, upload, mobile resize, nested draft galleries, public carousel navigation and mobile layout",
    );
  } finally {
    await browser.close();
    server.kill();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

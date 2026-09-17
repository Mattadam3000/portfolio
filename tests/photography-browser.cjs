// Run with Node and Playwright installed. GitHub is mocked; no publishing occurs.
// Optional PLAYWRIGHT_MODULE and CHROMIUM_EXECUTABLE_PATH select local browser binaries.
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const {spawn} = require('child_process');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const live = JSON.parse(fs.readFileSync(path.join(root, 'photography.json')));
const projects = live.projects.filter(p => p.published !== false);
const project = projects.find(p => p.images.length > 2);
const projectIndex = projects.indexOf(project);
const nextProject = projects[projectIndex + 1];
const single = projects.find(p => p.images.length === 1);
const base = 'http://localhost:8765';
const pause = page => page.waitForTimeout(650);
async function mock(page) {
 await page.route('https://api.github.com/**', route => {
  assert.equal(route.request().method(), 'GET');
  const p = new URL(route.request().url()).pathname;
  return route.fulfill({json:p === '/user' ? {id:164549058} : p.endsWith('/portfolio') ? {permissions:{push:true}} : {sha:'base',content:Buffer.from(JSON.stringify(live)).toString('base64')}});
 });
}
async function active(view) {
 return view.locator('#projects').evaluate(track => {
  const slide = track.children[Math.round(track.scrollLeft / track.clientWidth)];
  return {project:slide.dataset.project,src:slide.querySelector('img')?.getAttribute('src')};
 });
}
(async () => {
 const server = spawn('python3',['-m','http.server','8765'],{cwd:root,stdio:'ignore'});
 await new Promise(r => setTimeout(r,500));
 const browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE_PATH || undefined,args:['--no-sandbox','--disable-dev-shm-usage'],headless:true});
 try {
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(`${base}/photography/${project.slug}/`);
  await pause(page);
  assert.equal((await active(page)).project,project.slug,'deep link opens selected collection');
  assert.equal(await page.locator('.gallery-dots button').count(),project.images.length);
  const before = await page.locator('.viewer-caption').boundingBox();
  assert(before.x>700,'title sits bottom right');
  const hit = await page.locator('.gallery-next').boundingBox();
  assert(hit.width>400,'next hit area is wide');
  // Click well inside the photo, away from the visible edge arrow.
  await page.mouse.click(1100,420);await pause(page);
  assert((await active(page)).src.endsWith(project.images[1].image));
  const after = await page.locator('.viewer-caption').boundingBox();
  assert(Math.abs(before.y+before.height-after.y-after.height)<1,'caption baseline stays fixed');
  assert(await page.locator('.gallery-dots button').first().evaluate(e=>getComputedStyle(e,'::after').width==='3px'));
  await page.locator('.gallery-dots button').last().click();await pause(page);
  await page.mouse.click(1100,420);await pause(page);
  assert.equal((await active(page)).project,nextProject.slug,'continues to next collection');
  await page.mouse.click(300,420);await pause(page);
  assert((await active(page)).src.endsWith(project.images.at(-1).image),'previous crosses back into collection');
  await page.screenshot({path:'/tmp/photography-viewer-desktop.png'});
  await page.goto(`${base}/photography/`);
  const multiSlide=page.locator(`.slide[data-project="${project.slug}"]`);
  assert.equal(await multiSlide.locator('.view-link').textContent(),'View collection ↗');
  assert.equal(await page.locator(`.slide[data-project="${single.slug}"] .view-link`).count(),0,'no CTA for single photo');
  await multiSlide.evaluate(e=>e.scrollIntoView());await pause(page);
  assert.equal(await page.locator('.viewer-caption .project-label span').first().textContent(),project.title);
  // Draft preview: repeatedly reorder, close/reopen, and use the continuous viewer.
  await mock(page);await page.goto(`${base}/photography/edit/`);
  await page.evaluate(async()=>{token='mock';await start();});
  for(let i=0;i<3;i++) {
   await page.locator('.card').first().getByRole('button',{name:'→',exact:true}).click();
   const title=await page.locator('.card input').first().inputValue();
   await page.locator('#preview').click();const frame=page.frameLocator('#preview-frame');
   await frame.locator('.viewer-caption').waitFor();
   assert.equal(await frame.locator('.viewer-caption .project-label span').first().textContent(),title);
   assert((await page.locator('#preview-frame').boundingBox()).height>500);
   await page.locator('#device').click();await page.locator('#close-preview').click();
  }
  await page.evaluate(slug=>{selected=slug;render();},project.slug);
  await page.locator('.card').first().getByRole('button',{name:'→',exact:true}).click();
  const expected=await page.locator('.card img').first().getAttribute('src');
  await page.locator('#preview').click();let frame=page.frameLocator('#preview-frame');await pause(page);
  assert((await active(frame)).src.endsWith(expected),'preview reflects image reorder');
  await frame.locator('.gallery-dots button').last().click();await pause(page);
  await frame.locator('.gallery-next').click();await pause(page);
  assert.notEqual((await active(frame)).project,project.slug,'preview moves between collections without closing');
  await frame.getByText('Back ↗',{exact:true}).click();await pause(page);
  assert(await frame.locator('html').evaluate(e=>e.classList.contains('portfolio')));
  await page.locator('#close-preview').click();
  await page.locator('#files').setInputFiles(root+project.images[0].image);
  await page.waitForFunction(()=>!busy);
  for(let i=0;i<2;i++) {
   await page.locator('#preview').click();frame=page.frameLocator('#preview-frame');await pause(page);
   await frame.locator('.gallery-dots button').last().click();await pause(page);
   assert((await active(frame)).src.startsWith('blob:'));
   assert(await frame.locator(`.slide[data-project="${project.slug}"] img`).last().evaluate(e=>e.complete&&e.naturalWidth>0));
   await page.locator('#close-preview').click();
  }
  // Native mobile swipe and a real touch-context editor preview.
  const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  await mobile.goto(`${base}/photography/${project.slug}/`);await pause(mobile);
  const cdp=await mobile.context().newCDPSession(mobile);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:320,y:420}]});
  for(let x=300;x>=60;x-=30){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:420}]});await mobile.waitForTimeout(25);}
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await pause(mobile);
  assert((await active(mobile)).src.endsWith(project.images[1].image),'mobile swipe');
  assert(await mobile.locator('body').evaluate(e=>e.scrollHeight<=innerHeight+1));
  await mobile.screenshot({path:'/tmp/photography-viewer-mobile.png'});
  await mock(mobile);await mobile.goto(`${base}/photography/edit/`);
  await mobile.evaluate(async slug=>{token='mock';await start();selected=slug;render();},project.slug);
  for(let i=0;i<2;i++) {
   await mobile.locator('.card').first().getByRole('button',{name:'→',exact:true}).click();
   await mobile.locator('#preview').click();const mf=mobile.frameLocator('#preview-frame');await pause(mobile);
   assert.equal((await active(mf)).project,project.slug);
   assert((await mobile.locator('#preview-frame').boundingBox()).height>500);
   await mobile.locator('#close-preview').click();
  }
  // Automatic publication refresh must leave a clean address and preserve anchors.
  await page.route('**/photography/version.json?*',route=>route.fulfill({json:{version:'abcdef0123456789'}}));
  const refreshed=page.waitForRequest(r=>r.isNavigationRequest()&&r.url().includes('v=abcdef0123456789'));
  await page.goto(`${base}/photography/`);await refreshed;await page.waitForLoadState('load');
  await page.waitForFunction(()=>!new URL(location.href).searchParams.has('v'));
  await page.goto(`${base}/photography/?v=abcdef0123456789#pink-bath`);
  await page.waitForFunction(()=>!new URL(location.href).searchParams.has('v'));
  assert.equal(new URL(page.url()).hash,'#pink-bath');
  assert.deepEqual(errors,[]);
  console.log('PASS: fixed captions, broad click areas, compact dots, continuous collections, mobile swipe, fresh private previews, uploads, and clean automatic refresh.');
 } finally {await browser.close();server.kill();}
})().catch(e=>{console.error(e);process.exit(1)});

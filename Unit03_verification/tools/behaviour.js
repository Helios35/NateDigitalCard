// Unit 01 + Unit 02 behaviour checks, plus the budgets (requests, weight, console).
// usage: node behaviour.js <baseUrl> <outDir>
// Real clock (no freezing) so the live-time check means something.
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [, , BASE, OUT] = process.argv;
const VIEWPORTS = {
  phone: { width: 390, height: 844, deviceScaleFactor: 3, isMobile: true, hasTouch: true },
  desktop: { width: 1440, height: 900, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function open(browser, vp, { reduced = false, share = 'stub', dl } = {}) {
  const ctx = await browser.createBrowserContext(dl ? { downloadBehavior: { policy: 'allow', downloadPath: dl } } : {});
  await ctx.overridePermissions(new URL(BASE).origin, ['clipboard-read', 'clipboard-write', 'clipboard-sanitized-write']);
  const page = await ctx.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport(VIEWPORTS[vp]);
  if (reduced) await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  await page.evaluateOnNewDocument((mode) => {
    if (mode === 'none') { delete Navigator.prototype.share; delete Navigator.prototype.canShare; }
    else { // record what the card hands the share sheet, and resolve as if shared
      window.__shared = [];
      Navigator.prototype.share = function (d) { window.__shared.push(d); return Promise.resolve(); };
    }
  }, share);
  const net = { requests: [], bytes: 0, console: [], errors: [] };
  const cdp = await page.createCDPSession();
  await cdp.send('Network.enable');
  cdp.on('Network.requestWillBeSent', (e) => net.requests.push(e.request.url));
  cdp.on('Network.loadingFinished', (e) => { net.bytes += e.encodedDataLength; });
  page.on('console', (m) => net.console.push(m.type() + ': ' + m.text()));
  page.on('pageerror', (e) => net.errors.push(String(e)));
  await page.goto(BASE, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await sleep(2500);
  return { ctx, page, cdp, net };
}

const state = (page) => page.evaluate(() => ({
  flipped: document.getElementById('hero').classList.contains('is-flipped'),
  videoPaused: document.getElementById('video').paused,
  frontInert: document.getElementById('front').inert,
  backInert: document.getElementById('back').inert,
  qrOpen: document.getElementById('qr-layer').classList.contains('is-open'),
  heroInert: document.getElementById('hero').inert,
  contentInert: document.getElementById('content').inert,
  locked: document.documentElement.classList.contains('is-locked'),
  focus: document.activeElement && (document.activeElement.id || document.activeElement.tagName),
  toast: document.getElementById('toast').classList.contains('is-shown') ? document.getElementById('toast').textContent : null,
}));

async function run(browser, vp) {
  const r = { vp };
  const dl = path.resolve(OUT, vp + '-download');
  fs.mkdirSync(dl, { recursive: true });
  let { ctx, page, net } = await open(browser, vp, { dl });

  // live time: label + America/Chicago time now
  r.time = await page.evaluate(() => ({
    shown: document.getElementById('eyebrow').textContent,
    expected: CARD.place.label + ' · ' + new Intl.DateTimeFormat('en-US', { timeZone: CARD.place.timeZone, hour: 'numeric', minute: '2-digit' }).format(new Date()),
  }));
  r.time.pass = r.time.shown === r.time.expected;

  // hero video
  r.video = await page.evaluate(() => { const v = document.getElementById('video'); return { src: v.getAttribute('src'), muted: v.muted, loop: v.loop, playsInline: v.playsInline, paused: v.paused, w: v.videoWidth, h: v.videoHeight, duration: v.duration, playing: v.classList.contains('is-playing') }; });

  // flip: tap/click on the hero, keyboard Enter and Space on the hint
  const flip = {};
  if (vp === 'phone') {
    const b = await page.evaluate(() => { const r = document.getElementById('flip').getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + 120 }; });
    await page.touchscreen.tap(b.x, b.y); await sleep(1000); flip.tapToBack = await state(page);
    await page.touchscreen.tap(b.x, b.y); await sleep(1000); flip.tapToFront = await state(page);
  } else {
    await page.mouse.click(700, 250); await sleep(1000); flip.clickToBack = await state(page);
    await page.mouse.click(700, 250); await sleep(1000); flip.clickToFront = await state(page);
    await page.mouse.move(3, 3);
  }
  await page.focus('#flip-to-back'); await page.keyboard.press('Enter'); await sleep(1000); flip.enterToBack = await state(page);
  await page.keyboard.press(' '); await sleep(1000); flip.spaceToFront = await state(page);
  r.flip = flip;

  // QR: open by click/tap and Enter; close by Esc, Close button, overlay
  const qr = {};
  await page.click('#qr-btn'); await sleep(400); qr.openClick = await state(page);
  await page.keyboard.press('Escape'); await sleep(400); qr.closeEsc = await state(page);
  await page.focus('#qr-btn'); await page.keyboard.press('Enter'); await sleep(400); qr.openEnter = await state(page);
  await page.keyboard.press('Enter'); await sleep(400); qr.closeButtonEnter = await state(page);
  await page.click('#qr-btn'); await sleep(400);
  qr.scrollYBefore = await page.evaluate(() => scrollY);
  await page.mouse.wheel({ deltaY: 400 }); await sleep(300);
  qr.scrollYWhileOpen = await page.evaluate(() => scrollY);
  await page.mouse.click(5, 5); await sleep(400); qr.closeOverlay = await state(page);
  qr.encodes = await page.evaluate(() => location.href.split('#')[0]);
  r.qr = qr;

  // Share: share-sheet path (stub records what the card hands over)
  await page.click('#share-btn'); await sleep(500);
  r.shareSheet = await page.evaluate(() => window.__shared);
  await sleep(3500);

  // Save: vCard download (photo arrives asynchronously first)
  await page.click('#save'); await sleep(1500);
  r.save = { toast: (await state(page)).toast, files: fs.readdirSync(dl), download: await page.evaluate(() => document.getElementById('save').download) };

  // Links
  r.links = await page.evaluate(() => [...document.querySelectorAll('#links > a')].map((a) => ({ text: a.innerText.replace(/\s+/g, ' ').trim(), href: a.href, target: a.target, rel: a.rel })));
  r.linksMatchCard = await page.evaluate(() => JSON.stringify([...document.querySelectorAll('#links > a')].map((a) => a.getAttribute('href'))) === JSON.stringify(CARD.links.map((l) => l.url)));
  r.net1 = net;
  await ctx.close();

  // Share: copy-link fallback when there is no share sheet
  ({ ctx, page, net } = await open(browser, vp, { share: 'none' }));
  await page.click('#share-btn'); await sleep(600);
  r.shareCopy = { toast: (await state(page)).toast, clipboard: await page.evaluate(() => navigator.clipboard.readText().catch((e) => 'ERR ' + e)) };
  await ctx.close();

  // Budgets: a clean first visit, no cache, nothing clicked
  ({ ctx, page, net } = await open(browser, vp));
  await sleep(4000);
  const origin = new URL(BASE).origin;
  r.budget = {
    requests: net.requests.length,
    outside: net.requests.filter((u) => !u.startsWith(origin) && !u.startsWith('data:') && !u.startsWith('blob:')),
    bytes: net.bytes, console: net.console, errors: net.errors,
  };
  await ctx.close();

  // Reduced motion: no video request
  ({ ctx, page, net } = await open(browser, vp, { reduced: true }));
  await sleep(1500);
  r.reduced = { videoRequested: net.requests.some((u) => u.endsWith('.mp4')), bytes: net.bytes, console: net.console, errors: net.errors };
  await ctx.close();
  return r;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--disable-gpu', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required'] });
  const all = {};
  try {
    for (const vp of Object.keys(VIEWPORTS)) all[vp] = await run(browser, vp);
  } finally { await browser.close(); }
  fs.writeFileSync(path.join(OUT, 'behaviour.json'), JSON.stringify(all, null, 1));
  console.log(JSON.stringify(all, null, 1));
})().catch((e) => { console.error(e); process.exit(1); });

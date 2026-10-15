// Deterministic state capture for the digital card.
// usage: node capture.js <baseUrl> <outDir>
// Freezes the clock (3:42 PM Chicago) and the hero video (paused at 1.0 s) so two runs
// of the same code produce byte-identical screenshots. Dumps every element's computed
// style (custom properties excluded) per state, so before/after can be diffed exactly.
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [, , BASE, OUT] = process.argv;
const FIXED = Date.parse('2026-10-15T20:42:00Z'); // 3:42 PM America/Chicago (CDT)

const VIEWPORTS = {
  phone: { width: 390, height: 844, deviceScaleFactor: 3, isMobile: true, hasTouch: true },
  desktop: { width: 1440, height: 900, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
};
// Every control, by a selector that does not depend on class names (classes may be refactored).
const CONTROLS = [
  { id: 'share-btn', sel: '#share-btn' },
  { id: 'qr-btn', sel: '#qr-btn' },
  { id: 'flip-to-back', sel: '#flip-to-back' },
  { id: 'save', sel: '#save' },
  { id: 'link-1', sel: '#links > a:nth-of-type(1)' },
  { id: 'link-2', sel: '#links > a:nth-of-type(2)' },
  { id: 'flip-to-front', sel: '#flip-to-front', needs: 'flipped' },
  { id: 'qr-close', sel: '#qr-close', needs: 'qr' },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const away = (page) => page.mouse.move(3, 3);

// In-page: stable element key from tag/id/nth-of-type path (no classes).
const DUMP_FN = `(function (rootSel) {
  function key(el) {
    const parts = [];
    while (el && el.nodeType === 1) {
      let i = 1, s = el;
      while ((s = s.previousElementSibling)) if (s.tagName === el.tagName) i++;
      parts.unshift(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + ':' + i);
      el = el.parentElement;
    }
    return parts.join('>');
  }
  const root = rootSel ? document.querySelector(rootSel) : document.body;
  const els = [root, ...root.querySelectorAll('*')];
  if (!rootSel) els.unshift(document.documentElement);
  const out = {};
  for (const el of els) {
    for (const pseudo of [null, '::before', '::after']) {
      const cs = getComputedStyle(el, pseudo);
      if (pseudo && (cs.content === 'none' || cs.content === 'normal')) continue;
      const o = {};
      for (let i = 0; i < cs.length; i++) { const p = cs[i]; if (!p.startsWith('--')) o[p] = cs.getPropertyValue(p); }
      out[key(el) + (pseudo || '')] = o;
    }
  }
  return out;
})`;

async function freezeVideo(page) {
  await page.evaluate(async () => {
    const v = document.getElementById('video');
    if (!v || !v.getAttribute('src')) return;
    if (v.readyState < 2) await new Promise((r) => v.addEventListener('loadeddata', r, { once: true }));
    v.pause();
    if (Math.abs(v.currentTime - 1.0) > 1e-3) {
      const p = new Promise((r) => v.addEventListener('seeked', r, { once: true }));
      v.currentTime = 1.0;
      await p;
    }
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
  await sleep(250);
}

async function newPage(browser, vp, opts = {}) {
  const ctx = await browser.createBrowserContext({ downloadBehavior: { policy: 'allow', downloadPath: path.resolve(OUT, vp, 'downloads') } });
  const origin = new URL(BASE).origin;
  await ctx.overridePermissions(origin, ['clipboard-read', 'clipboard-write', 'clipboard-sanitized-write']);
  const page = await ctx.newPage();
  await page.setCacheEnabled(false);
  await page.setViewport(VIEWPORTS[vp]);
  if (opts.reduced) await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  await page.evaluateOnNewDocument((fixed) => {
    const RealDate = Date;
    class FakeDate extends RealDate {
      constructor(...a) { if (a.length === 0) super(fixed); else super(...a); }
      static now() { return fixed; }
    }
    window.Date = FakeDate;
    // No OS share sheet in a headless run: exercise the card's copy-link fallback instead.
    delete Navigator.prototype.share; delete Navigator.prototype.canShare;
  }, FIXED);
  const log = { requests: [], console: [], pageErrors: [], failed: [] };
  page.on('request', (r) => log.requests.push(r.url()));
  page.on('requestfailed', (r) => log.failed.push(r.url() + ' ' + (r.failure() && r.failure().errorText)));
  page.on('console', (m) => log.console.push(m.type() + ': ' + m.text()));
  page.on('pageerror', (e) => log.pageErrors.push(String(e)));
  const cdp = await page.createCDPSession();
  await page.goto(BASE, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  if (!opts.reduced) {
    await page.waitForFunction(() => document.getElementById('video').classList.contains('is-playing'), { timeout: 15000 });
  }
  await sleep(1300); // entrance (0.6 s) and poster→video fade (0.4 s) finish
  await away(page);
  await freezeVideo(page);
  await sleep(300);
  return { page, ctx, cdp, log };
}

async function shot(page, file, clipSel, pad = 14) {
  if (!clipSel) return page.screenshot({ path: file, fullPage: true });
  const box = await page.evaluate((s) => {
    const r = document.querySelector(s).getBoundingClientRect();
    return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height };
  }, clipSel);
  return page.screenshot({
    path: file, captureBeyondViewport: true,
    clip: { x: Math.max(0, box.x - pad), y: Math.max(0, box.y - pad), width: box.w + pad * 2, height: box.h + pad * 2 },
  });
}

const dump = (page, sel) => page.evaluate(`${DUMP_FN}(${sel ? JSON.stringify(sel) : 'null'})`);

async function nodeId(cdp, sel) {
  const { root } = await cdp.send('DOM.getDocument', { depth: -1 });
  const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: sel });
  return nodeId;
}

async function enter(page, state) {
  if (state === 'flipped') {
    await page.click('#flip-to-back');
    await away(page);
    await sleep(1300);
  } else if (state === 'qr') {
    await page.click('#qr-btn');
    await away(page);
    await sleep(700);
  }
}
async function leave(page, state) {
  if (state === 'flipped') { await page.click('#flip-to-front'); await away(page); await sleep(1300); await freezeVideo(page); }
  else if (state === 'qr') { await page.keyboard.press('Escape'); await sleep(500); }
  await page.evaluate(() => document.activeElement && document.activeElement.blur());
}

async function run(browser, vp) {
  const dir = path.join(OUT, vp);
  fs.mkdirSync(path.join(dir, 'downloads'), { recursive: true });
  const meta = { vp, media: {}, tabOrder: [], toasts: {} };
  const save = (name, data) => fs.writeFileSync(path.join(dir, name), JSON.stringify(data, null, 1));

  // ---- 1. whole-page states ----
  let { page, ctx, cdp, log } = await newPage(browser, vp);
  meta.media = await page.evaluate(() => ({
    pointerCoarse: matchMedia('(pointer: coarse)').matches,
    hover: matchMedia('(hover: hover)').matches,
    eyebrow: document.getElementById('eyebrow').textContent,
    fonts: ['Inter', 'Playfair Display', 'JetBrains Mono'].map((f) => [f, document.fonts.check('16px "' + f + '"')]),
    hasShare: typeof navigator.share,
  }));
  await shot(page, path.join(dir, 'front.png'));
  save('styles-front.json', await dump(page));

  await enter(page, 'flipped');
  await shot(page, path.join(dir, 'flipped.png'));
  save('styles-flipped.json', await dump(page));
  await leave(page, 'flipped');

  await enter(page, 'qr');
  await shot(page, path.join(dir, 'qr.png'));
  await page.screenshot({ path: path.join(dir, 'qr-viewport.png') });
  await shot(page, path.join(dir, 'qr-tile.png'), '#qr-tile', 0);
  save('styles-qr.json', await dump(page));
  await leave(page, 'qr');

  // Share → toast (copy fallback when there is no share sheet)
  await page.click('#share-btn');
  await away(page);
  await sleep(900);
  meta.toasts.share = await page.evaluate(() => ({ text: document.getElementById('toast').textContent, shown: document.getElementById('toast').classList.contains('is-shown') }));
  await page.screenshot({ path: path.join(dir, 'toast-share.png') });
  save('styles-toast.json', await dump(page));
  await sleep(3800);

  // Save → download + toast
  await page.click('#save');
  await away(page);
  await sleep(1000);
  meta.toasts.save = await page.evaluate(() => ({ text: document.getElementById('toast').textContent, shown: document.getElementById('toast').classList.contains('is-shown') }));
  await page.screenshot({ path: path.join(dir, 'toast-save.png') });
  await sleep(3800);

  // ---- 2. real keyboard focus on every control (fresh page, so Tab starts at the top) ----
  meta.log = log;
  await ctx.close();
  ({ page, ctx, cdp, log } = await newPage(browser, vp));
  for (let i = 0; i < 8; i++) {
    await page.keyboard.press('Tab');
    await sleep(600);
    const id = await page.evaluate(() => {
      const a = document.activeElement;
      if (!a || a === document.body) return null;
      if (a.id) return a.id;
      const links = [...document.querySelectorAll('#links > a')];
      return links.includes(a) ? 'link-' + (links.indexOf(a) + 1) : a.tagName;
    });
    if (!id || meta.tabOrder.includes(id)) break;
    meta.tabOrder.push(id);
    const c = CONTROLS.find((x) => x.id === id);
    await shot(page, path.join(dir, `focus-${id}.png`), c ? c.sel : null);
    save(`styles-focus-${id}.json`, await dump(page, c ? c.sel : null));
  }
  // flip by keyboard: focus moves to the back's hint
  await page.focus('#flip-to-back');
  await page.keyboard.press('Enter');
  await sleep(1100);
  meta.afterFlipFocus = await page.evaluate(() => document.activeElement.id);
  await shot(page, path.join(dir, 'focus-flip-to-front.png'), '#flip-to-front');
  save('styles-focus-flip-to-front.json', await dump(page, '#flip-to-front'));
  await page.keyboard.press('Enter');
  await sleep(1100);
  meta.afterFlipBackFocus = await page.evaluate(() => document.activeElement.id);
  await freezeVideo(page);
  // QR by keyboard: focus moves to Close, Esc returns it to the QR button
  await page.focus('#qr-btn');
  await page.keyboard.press('Enter');
  await sleep(500);
  meta.qrOpenFocus = await page.evaluate(() => document.activeElement.id);
  await shot(page, path.join(dir, 'focus-qr-close.png'), '#qr-close');
  save('styles-focus-qr-close.json', await dump(page, '#qr-close'));
  await page.keyboard.press('Escape');
  await sleep(500);
  meta.qrCloseFocus = await page.evaluate(() => document.activeElement.id);
  await page.evaluate(() => document.activeElement && document.activeElement.blur());

  // ---- 3. forced hover / active, and disabled, on every control ----
  await cdp.send('DOM.enable');
  await cdp.send('CSS.enable');
  for (const c of CONTROLS) {
    if (c.needs) await enter(page, c.needs);
    for (const st of ['hover', 'active']) {
      const nid = await nodeId(cdp, c.sel);
      await cdp.send('CSS.forcePseudoState', { nodeId: nid, forcedPseudoClasses: [st] });
      await sleep(600);
      await shot(page, path.join(dir, `${st}-${c.id}.png`), c.sel);
      save(`styles-${st}-${c.id}.json`, await dump(page, c.sel));
      await cdp.send('CSS.forcePseudoState', { nodeId: nid, forcedPseudoClasses: [] });
      await sleep(400);
    }
    if (c.needs) await leave(page, c.needs);
  }
  // disabled: Save loses its href (its only failure path); icon button gets [disabled]
  await page.evaluate(() => { const s = document.getElementById('save'); s.dataset.href = s.getAttribute('href'); s.removeAttribute('href'); document.getElementById('share-btn').disabled = true; });
  await sleep(300);
  await shot(page, path.join(dir, 'disabled-save.png'), '#save');
  await shot(page, path.join(dir, 'disabled-share-btn.png'), '#share-btn');
  save('styles-disabled-save.json', await dump(page, '#save'));
  save('styles-disabled-share-btn.json', await dump(page, '#share-btn'));
  await page.evaluate(() => { const s = document.getElementById('save'); s.setAttribute('href', s.dataset.href); delete s.dataset.href; document.getElementById('share-btn').disabled = false; });

  meta.log2 = log;
  await ctx.close();

  // ---- 4. reduced motion ----
  ({ page, ctx, log } = await newPage(browser, vp, { reduced: true }));
  meta.reduced = await page.evaluate(() => ({
    videoSrc: document.getElementById('video').getAttribute('src'),
    durations: [...new Set([...document.querySelectorAll('*')].flatMap((e) => [getComputedStyle(e).transitionDuration, getComputedStyle(e, '::before').transitionDuration]))],
    delays: [...new Set([...document.querySelectorAll('*')].map((e) => getComputedStyle(e).transitionDelay))],
    animations: [...new Set([...document.querySelectorAll('*')].map((e) => getComputedStyle(e).animationName))],
  }));
  await shot(page, path.join(dir, 'reduced.png'));
  save('styles-reduced.json', await dump(page));
  meta.reducedLog = log;
  await ctx.close();

  save('run.json', meta);
  return meta;
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: true,
    args: ['--disable-gpu', '--force-color-profile=srgb', '--hide-scrollbars', '--font-render-hinting=none',
      '--autoplay-policy=no-user-gesture-required', '--disable-features=MediaSessionService'],
  });
  try {
    for (const vp of Object.keys(VIEWPORTS)) {
      const m = await run(browser, vp);
      console.log(vp, JSON.stringify({ media: m.media, tabOrder: m.tabOrder, toasts: m.toasts, afterFlipFocus: m.afterFlipFocus, afterFlipBackFocus: m.afterFlipBackFocus, qrOpenFocus: m.qrOpenFocus, qrCloseFocus: m.qrCloseFocus, reduced: m.reduced, errors: m.log.pageErrors, console: m.log.console }));
    }
  } finally {
    await browser.close();
  }
})().catch((e) => { console.error(e); process.exit(1); });

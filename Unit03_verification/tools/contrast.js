// WCAG 2 contrast, measured in the browser against the pixels actually painted behind each
// piece of text or mark. Text is hidden (colour transparent, shadows off, SVGs hidden), the
// page is screenshotted, and every pixel inside the text's box is tested against the text's
// computed colour (composited by its opacity). Worst pixel wins.
// usage: node contrast.js <baseUrl> <outDir>
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const { PNG } = require('pngjs');

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [, , BASE, OUT] = process.argv;
const VIEWPORTS = {
  phone: { width: 390, height: 1400, deviceScaleFactor: 3, isMobile: true, hasTouch: true },
  desktop: { width: 1440, height: 1400, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const HIDE = `*, *::before, *::after { color: transparent !important; -webkit-text-fill-color: transparent !important; text-shadow: none !important; }
svg { visibility: hidden !important; }`;

// ---- colour maths ----
const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
const lum = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
const parse = (s) => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
const over = (fg, a, bg) => [0, 1, 2].map((i) => fg[i] * a + bg[i] * (1 - a));
const hex = (c) => '#' + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();

// ---- in page: every visible text run and SVG mark inside a scope ----
const COLLECT = `(function (scopeSel) {
  const scope = document.querySelector(scopeSel);
  const out = [];
  const vis = (el) => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && el.getClientRects().length > 0; };
  const alpha = (el) => { let a = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) a *= parseFloat(getComputedStyle(e).opacity); return a; };
  const name = (el) => (el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : ''));
  const label = (el) => { const p = []; for (let e = el; e && e !== scope.parentElement && p.length < 3; e = e.parentElement) p.unshift(name(e)); return p.join(' > '); };
  function walk(el) {
    if (!vis(el)) return;
    if (el.tagName.toLowerCase() === 'svg') {
      const r = el.getBoundingClientRect();
      out.push({ kind: 'mark', label: label(el), color: getComputedStyle(el).color, alpha: alpha(el), rect: [r.left, r.top, r.width, r.height] });
      return;
    }
    const texts = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
    if (texts.length) {
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      for (const t of texts) { const rg = document.createRange(); rg.selectNodeContents(t); for (const r of rg.getClientRects()) { x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); } }
      const cs = getComputedStyle(el);
      out.push({ kind: 'text', label: label(el), text: texts.map((t) => t.textContent.trim()).join(' ').slice(0, 40), color: cs.color, alpha: alpha(el), size: cs.fontSize, weight: cs.fontWeight, rect: [x0, y0, x1 - x0, y1 - y0] });
    }
    for (const c of el.children) walk(c);
  }
  walk(scope);
  return out;
})`;

// Screenshot only the region that matters (CSS px, page has no scroll at this viewport height).
// Returns the PNG plus its origin in device pixels, so callers index the same pixels as a full shot.
async function grab(page, x0, y0, x1, y1) {
  const dpr = page.viewport().deviceScaleFactor;
  const vw = page.viewport().width, vh = page.viewport().height;
  const cx0 = Math.max(0, Math.floor(x0) - 2), cy0 = Math.max(0, Math.floor(y0) - 2);
  const cx1 = Math.min(vw, Math.ceil(x1) + 2), cy1 = Math.min(vh, Math.ceil(y1) + 2);
  const png = PNG.sync.read(await page.screenshot({ type: 'png', clip: { x: cx0, y: cy0, width: cx1 - cx0, height: cy1 - cy0 } }));
  return { png, ox: Math.round(cx0 * dpr), oy: Math.round(cy0 * dpr), dpr };
}

async function measure(page, scopeSel, extra = []) {
  const items = (await page.evaluate(`${COLLECT}(${JSON.stringify(scopeSel)})`)).concat(extra);
  if (!items.length) return [];
  const style = await page.addStyleTag({ content: HIDE });
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const bx0 = Math.min(...items.map((i) => i.rect[0])), by0 = Math.min(...items.map((i) => i.rect[1]));
  const bx1 = Math.max(...items.map((i) => i.rect[0] + i.rect[2])), by1 = Math.max(...items.map((i) => i.rect[1] + i.rect[3]));
  const { png, ox, oy, dpr } = await grab(page, bx0, by0, bx1, by1);
  await page.evaluate((s) => s.remove(), style);
  // Unhiding runs the controls' 150ms colour transition back from transparent; let it finish
  // so the next measurement reads the real colour, not a mid-fade one.
  await sleep(250);
  return items.map((it) => {
    const c = parse(it.color);
    const [x, y, w, h] = it.rect.map((v) => v * dpr);
    let worst = Infinity, worstBg = null, minL = Infinity, maxL = -Infinity, n = 0;
    for (let yy = Math.max(oy, Math.floor(y)); yy < Math.min(oy + png.height, Math.ceil(y + h)); yy++) {
      for (let xx = Math.max(ox, Math.floor(x)); xx < Math.min(ox + png.width, Math.ceil(x + w)); xx++) {
        const i = ((yy - oy) * png.width + (xx - ox)) * 4;
        const bg = [png.data[i], png.data[i + 1], png.data[i + 2]];
        const fg = over(c, c[3] * it.alpha, bg);
        const r = ratio(fg, bg);
        n++;
        const L = lum(bg); minL = Math.min(minL, L); maxL = Math.max(maxL, L);
        if (r < worst) { worst = r; worstBg = bg; }
      }
    }
    const need = it.kind === 'text' ? 4.5 : 3;
    return { kind: it.kind, label: it.label, text: it.text, fg: hex(c) + (c[3] * it.alpha < 1 ? ` @${+(c[3] * it.alpha).toFixed(2)}` : ''), worstBg: worstBg && hex(worstBg), pixels: n, ratio: +worst.toFixed(2), need, pass: worst >= need };
  });
}

// The focus ring as a mark: ring colour against the pixels just outside it (4–6 px beyond the box).
async function ringRatio(page, sel, inset) {
  const info = await page.evaluate((s) => { const e = document.querySelector(s); const r = e.getBoundingClientRect(); return { rect: [r.left, r.top, r.width, r.height], shadow: getComputedStyle(e).boxShadow }; }, sel);
  const cols = [...info.shadow.matchAll(/rgba?\([^)]+\)/g)].map((m) => parse(m[0]));
  const ring = cols[cols.length - 1];
  const [x, y, w, h] = info.rect;
  const pad = inset + 5;
  const { png, ox, oy, dpr } = await grab(page, x - pad, y - pad, x + w + pad, y + h + pad);
  let worst = Infinity, worstBg = null;
  for (let d = inset + 1; d <= inset + 3; d++) {
    const pts = [];
    for (let t = 0; t <= 1; t += 0.02) { pts.push([x - d + (w + 2 * d) * t, y - d], [x - d + (w + 2 * d) * t, y + h + d - 0.5], [x - d, y - d + (h + 2 * d) * t], [x + w + d - 0.5, y - d + (h + 2 * d) * t]); }
    for (const [px, py] of pts) {
      const xx = Math.round(px * dpr) - ox, yy = Math.round(py * dpr) - oy;
      if (xx < 0 || yy < 0 || xx >= png.width || yy >= png.height) continue;
      const i = (yy * png.width + xx) * 4;
      const bg = [png.data[i], png.data[i + 1], png.data[i + 2]];
      const r = ratio(ring, bg);
      if (r < worst) { worst = r; worstBg = bg; }
    }
  }
  return { kind: 'ring', label: sel + ' focus ring', fg: hex(ring), worstBg: worstBg && hex(worstBg), ratio: +worst.toFixed(2), need: 3, pass: worst >= 3 };
}

async function open(browser, vp, reduced) {
  const ctx = await browser.createBrowserContext();
  await ctx.overridePermissions(new URL(BASE).origin, ['clipboard-read', 'clipboard-write', 'clipboard-sanitized-write']);
  const page = await ctx.newPage();
  await page.setViewport(VIEWPORTS[vp]);
  if (reduced) await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  await page.evaluateOnNewDocument(() => { delete Navigator.prototype.share; delete Navigator.prototype.canShare; });
  await page.goto(BASE, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await sleep(2000);
  await page.mouse.move(2, 2);
  const cdp = await page.createCDPSession();
  await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
  return { ctx, page, cdp };
}
async function force(cdp, sel, classes) {
  const { root } = await cdp.send('DOM.getDocument', { depth: -1 });
  const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: sel });
  await cdp.send('CSS.forcePseudoState', { nodeId, forcedPseudoClasses: classes });
  await sleep(400);
}
async function freeze(page, t) {
  await page.evaluate(async (t) => {
    const v = document.getElementById('video');
    v.pause();
    const p = new Promise((r) => v.addEventListener('seeked', r, { once: true }));
    v.currentTime = t; await p;
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, t);
  await sleep(60);
}

const CONTROLS = [
  { id: 'share-btn', sel: '#share-btn', video: true },
  { id: 'qr-btn', sel: '#qr-btn', video: true },
  { id: 'flip-to-back', sel: '#flip-to-back', video: true },
  { id: 'save', sel: '#save', ringInset: 5 },
  { id: 'link-1', sel: '#links > a:nth-of-type(1)' },
  { id: 'link-2', sel: '#links > a:nth-of-type(2)' },
  { id: 'flip-to-front', sel: '#flip-to-front', needs: 'flipped' },
  { id: 'qr-close', sel: '#qr-close', needs: 'qr' },
];

async function run(browser, vp) {
  const rows = [];
  const add = (state, list) => list.forEach((r) => rows.push({ vp, state, ...r }));
  let { ctx, page, cdp } = await open(browser, vp);
  await freeze(page, 1.0);

  // ---- surfaces at rest ----
  add('front, rest', await measure(page, '.card'));
  await page.click('#flip-to-back'); await page.mouse.move(2, 2); await sleep(1300);
  add('flipped, rest', await measure(page, '#back'));
  await page.click('#flip-to-front'); await page.mouse.move(2, 2); await sleep(1300); await freeze(page, 1.0);
  await page.click('#qr-btn'); await page.mouse.move(2, 2); await sleep(600);
  add('QR sheet, rest', await measure(page, '#qr'));
  await page.keyboard.press('Escape'); await sleep(500);
  await page.click('#share-btn'); await page.mouse.move(2, 2); await sleep(500);
  add('toast', await measure(page, '#toast'));
  await sleep(3800);
  await page.evaluate(() => document.activeElement.blur());

  // ---- every control in every state ----
  const states = vp === 'desktop' ? ['hover', 'active', 'focus-visible'] : ['active', 'focus-visible'];
  for (const c of CONTROLS) {
    if (c.needs === 'flipped') { await page.click('#flip-to-back'); await page.mouse.move(2, 2); await sleep(1300); }
    if (c.needs === 'qr') { await page.click('#qr-btn'); await page.mouse.move(2, 2); await sleep(600); }
    for (const st of states) {
      await force(cdp, c.sel, st === 'focus-visible' ? ['focus', 'focus-visible'] : [st]);
      add(`${c.id}: ${st}`, await measure(page, c.sel));
      if (st === 'focus-visible') rows.push({ vp, state: `${c.id}: focus-visible`, ...(await ringRatio(page, c.sel, c.ringInset || 3)) });
      await force(cdp, c.sel, []);
    }
    if (c.needs === 'flipped') { await page.click('#flip-to-front'); await page.mouse.move(2, 2); await sleep(1300); await freeze(page, 1.0); }
    if (c.needs === 'qr') { await page.keyboard.press('Escape'); await sleep(500); await page.evaluate(() => document.activeElement.blur()); }
  }

  // ---- over the video: 40 points across the 5.0 s clip, every front-face label and control state ----
  const video = [];
  const vstates = vp === 'desktop' ? ['rest', 'hover', 'active', 'focus-visible'] : ['rest', 'active', 'focus-visible'];
  for (let k = 0; k < 40; k++) {
    const t = +(k * 0.125).toFixed(3);
    await freeze(page, t);
    for (const r of await measure(page, '.front-text')) video.push({ t, state: 'rest', ...r });
    for (const c of CONTROLS.filter((x) => x.video)) {
      for (const st of vstates) {
        if (st !== 'rest') await force(cdp, c.sel, st === 'focus-visible' ? ['focus', 'focus-visible'] : [st]);
        for (const r of await measure(page, c.sel)) video.push({ t, state: st, ...r });
        if (st === 'focus-visible') video.push({ t, state: st, ...(await ringRatio(page, c.sel, 3)) });
        if (st !== 'rest') await force(cdp, c.sel, []);
      }
    }
  }
  await ctx.close();
  // the poster (what shows before the video plays, and always under reduced motion)
  ({ ctx, page, cdp } = await open(browser, vp, true));
  for (const r of await measure(page, '.front-text')) video.push({ t: 'poster', state: 'rest', ...r });
  for (const c of CONTROLS.filter((x) => x.video)) for (const r of await measure(page, c.sel)) video.push({ t: 'poster', state: 'rest', ...r });
  await ctx.close();

  // worst case per element+state over all frames
  const worst = {};
  for (const r of video) {
    const k = `${r.state} | ${r.label}${r.kind === 'ring' ? '' : ' (' + r.kind + ')'}`;
    if (!worst[k] || r.ratio < worst[k].ratio) worst[k] = { vp, key: k, fg: r.fg, worstBg: r.worstBg, ratio: r.ratio, at: r.t, need: r.need, pass: r.ratio >= r.need };
  }
  return { rows, video: Object.values(worst), frames: video.length };
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--disable-gpu', '--force-color-profile=srgb', '--hide-scrollbars', '--autoplay-policy=no-user-gesture-required'] });
  const all = {};
  try { for (const vp of Object.keys(VIEWPORTS)) all[vp] = await run(browser, vp); }
  finally { await browser.close(); }
  fs.writeFileSync(path.join(OUT, 'contrast.json'), JSON.stringify(all, null, 1));
  // plain-text report
  const lines = [];
  for (const [vp, d] of Object.entries(all)) {
    lines.push(`== ${vp}: surfaces and states (${d.rows.length} measurements)`);
    for (const r of d.rows) lines.push(`${r.pass ? 'PASS' : 'FAIL'} ${String(r.ratio).padStart(6)} (need ${r.need})  ${r.state.padEnd(26)} ${r.kind.padEnd(4)} ${r.fg.padEnd(13)} on ${String(r.worstBg).padEnd(8)} ${r.label}${r.text ? ' "' + r.text + '"' : ''}`);
    lines.push(`== ${vp}: over the video, worst of ${d.frames} measurements (40 frames + poster)`);
    for (const r of d.video) lines.push(`${r.pass ? 'PASS' : 'FAIL'} ${String(r.ratio).padStart(6)} (need ${r.need})  at ${String(r.at).padEnd(6)} ${r.fg.padEnd(13)} on ${String(r.worstBg).padEnd(8)} ${r.key}`);
  }
  fs.writeFileSync(path.join(OUT, 'contrast.txt'), lines.join('\n') + '\n');
  const fails = Object.values(all).flatMap((d) => d.rows.concat(d.video)).filter((r) => !r.pass);
  console.log(`measurements: ${Object.values(all).reduce((n, d) => n + d.rows.length + d.frames, 0)}; failures: ${fails.length}`);
  fails.forEach((f) => console.log('FAIL', JSON.stringify(f)));
})().catch((e) => { console.error(e); process.exit(1); });

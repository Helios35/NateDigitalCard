# Unit 02 — Build Notes: Digital Card, Zen Linen rebrand

**Brief:** Unit 02, Digital Card Zen Linen rebrand (colours, type and components), 2026-10-15
**Built:** 2026-10-15
**Branch:** `rebrand-zen-linen` (Nate merges)
**Build folder:** `C:\Users\nteiv\OneDrive\Documents\Projects\Digital Card_Nate`
**Status:** Built and verified by the builder in headless Chrome at 390 px and 1440 px. Waiting on Nate's review at the merge gate. Not yet checked on a real phone.

---

## What shipped
The card now uses nextsketch.com's brand, with the same behaviour as Unit 01:
- **Colour:** only fin's dark set. Charcoal surfaces, linen text, stone for the primary button and the focus ring, and coral as the one accent.
- **Type:** Playfair Display for the name and the flip-side line, Inter for the interface, JetBrains Mono for labels. Space Grotesk is gone.
- **Components:** every one was rebuilt to its fin recipe (shape, radius, border, surface, type, and hover, focus-visible, active and disabled states). None was only recoloured.
- **Media:** the new portrait clip with the soft coral glow, its poster and contact photo, the linen logo, and new icons, all from the kit, byte for byte.
- **Words:** the new flip-side words, badges and meta description.
- **Still true from Unit 01:** a single static page with no build step, no dependencies and zero outside requests.

## The one place to edit
Still **the top of `index.html`, between `EDIT THIS CARD` and `END EDIT`**. One field is new:
- `back.lineAccent`: the part of `back.line` shown in coral. It must appear in `line` word for word. Leave it empty to show the whole line in linen.

## Components: fin reference and what changed
| Component | Fin reference | What changed |
|---|---|---|
| Save | `button.tsx` default (primary) | Gold gradient pill with glow → flat stone `--primary` fill, `--primary-foreground` text, `radius-md` (6.4 px), Inter 500. Hover `primary/90`, active `primary/80`, focus ring, disabled 50%. Full width, **48 px tall** (see deviation 4). |
| Share, QR | `button.tsx` outline variant, icon size | 38 px gold circles → **36 px** squares with `radius-md` (**44 px on touch**). Border `--input`, fill `input/30`, hover `input/50`, active `--muted`, linen glyph 16 px, `shadow-xs`. They no longer change colour when the card flips, because both sides are dark now. |
| QR sheet | `dialog.tsx` | A cream-and-surface cover over the card → fin's dialog: a `black/50` overlay over the page, then a centred panel with `--background` fill, `--border` hairline, `radius-lg`, `shadow-lg` and 24 px padding. It fades and scales from 95% in 150 ms. Close button per `dialog.tsx`: `radius-md`, 28 px (44 px on touch), 70% opacity rising to 100%. Heading is fin's eyebrow label, name in Playfair, caption `text-sm` muted. |
| QR tile | (scan floor) | Linen `--foreground` tile, `--background` modules (14.4:1), `radius-md`. Same 4-module quiet zone as before. |
| Link rows | fin card surface | `--card` fill, `--border` hairline, `radius-lg` (8 px), 12×16 padding. Name Inter 500, sub-line muted `text-xs`, coral icon, muted arrow. Hover `--secondary` with `--accent` border and the arrow lifts to linen. Active `--muted`, and the sub-line and arrow lift to linen (see the contrast note). |
| Flip panel (back) | fin card surface | Cream → `--card` with a `--border` hairline where it meets the card. Linen logo, Playfair 700 line with coral "work in production", muted Inter body. |
| "Tap" hint | `button.tsx` ghost | Bare text → ghost control: `radius-md`, muted text, hover `accent/50` with linen text, active `--accent`, focus ring, 44 px tall on touch. Mono 11 px. |
| Toast | fin card surface | Warm brown → `--card`, `--border`, `radius-lg`, `shadow-lg`, `text-sm`. 150 ms in and out. |
| Badges | none in fin (extended) | Gold outline pill with glowing dot → fin's pill shape (`rounded-full`) on `--secondary` with a `--border` hairline. Linen mono 11 px label and **the site's own marker: a 6 px coral diamond** (the 45° square from nextsketch.com's service list). |
| Hero frame (card) | fin radius scale and border rule | 24 px radius, gold hairline and gold-tinted gradient → `radius-xl` (11.2 px), `--border` hairline, flat `--background`, `shadow-xl` (barely shows in dark, by design). |
| Divider, footer | fin eyebrow and muted text | The "Follow along" label is fin's eyebrow (muted, 11 px, uppercase, tracked), with `--border` lines. Footer uses the linen logo and muted text. |
| Quick-action tiles (off until P2) | fin card surface | Restyled to match the link rows, so P2 needs no styling work. |

## Visual calls (mine, each with its reason)
1. **Page background is `--sidebar` `#101010`, the card is `--background` `#141414`, and surfaces on it are `--card` `#1C1C1C`.** That gives three of fin's dark steps, so link rows and the flip panel lift off the card the way fin cards lift off a page. Inside the card it is the same charcoal as the site's page. `theme-color` is `#101010` to match the page.
2. **The warm radial page gradient is gone, with no replacement.** Fin's surfaces are flat, and the border does the separating.
3. **The hero overlay fades the clip into the card's own `--background`:** clear to 34%, 60% at 60%, 90% at 76%, solid at the bottom. It is tuned so every label over the video passes on every sampled frame (numbers below).
4. **Where coral lands** (it replaces gold, it doesn't spread):
   - the live "Chicago · time" label,
   - the badge diamonds,
   - the two link-row icons (marks),
   - "work in production",
   - the pencil lead in the logo (from the kit).

   Places that were gold and are **not** coral now:
   - icon buttons (linen, fin outline),
   - Save (stone, fin primary),
   - the "Follow along" and QR labels (muted, fin eyebrow),
   - badge text (linen),
   - link arrows (muted),
   - focus (stone ring, per the brief),
   - all glows and shadows (removed).
5. **Type sizes:**
   - Name: Playfair 700, 38 px, −0.025 em. The site's h1 uses the same weight and tracking.
   - Flip-side line: 27 px, balanced wrapping.
   - Every mono label: fin's one sub-12 px step (11 px), with the site's 0.12 em mono tracking. Unit 01 used four sizes between 10 and 11 px.
6. **Focus is fin's ring:** `--ring` at full opacity, 3 px, plus `border-color: --ring`, with a forced-colors outline fallback. On the stone Save button the ring sits 2 px off the fill (in `--background`); otherwise a stone ring on a stone button would just look like a bigger button.
7. **Motion:**
   - Every restyled state change is 150 ms (fin's number, under §8's 200 ms).
   - The flip (0.7 s), the entrance (0.6 s) and the poster-to-video fade (0.4 s) keep Unit 01's timing.
   - Reduced motion removes every transition, using fin's global rule.
8. **Hover styles apply only where the pointer can hover** (`@media (hover: hover)`), so a tapped link row doesn't stay "hovered" when you come back from LinkedIn. Press states apply everywhere.
9. **Touch floor (fin §9.6):** on a coarse pointer the icon buttons, the "Tap" hint and the QR close button grow to 44 px. Buttons stay 8 px apart.

## Contrast (measured with a tool: WCAG 2 formula, composited)
Full tables are in `Unit02_verification/checks/`.

| Pair | Ratio | Use |
|---|---|---|
| Linen on `#141414` / `#1C1C1C` / `#222222` | 14.41 / 13.33 / 12.45 | Text, badge text |
| Muted on `#141414` / `#1C1C1C` / `#222222` | 5.36 / 4.96 / 4.63 | Secondary text, row sub-line at rest and on hover |
| Muted on `#2A2A2A` | **4.18, fails** | Never used: a pressed row lifts its sub-line to linen (11.23) |
| Coral on `#141414` / `#1C1C1C` / `#222222` | 6.09 / 5.63 / 5.26 | Link icons, "work in production", badge diamonds |
| `#363636` on stone (rest / hover / active) | 7.71 / 6.35 / 5.15 | Save label |
| Stone ring on `#141414` / `#1C1C1C` / over video | 11.75 / 10.87 / 11.4+ | Focus |
| `#141414` modules on linen tile | 14.41 | QR |

**Text over the video** was captured with the text hidden, at 40 points across the clip plus the poster, at both widths. Each ratio is against the single brightest pixel behind the text:

| Text | Worst ratio |
|---|---|
| Coral time label | **5.25** |
| Muted "Tap" | 5.26 |
| "Tap" icon | 5.26 |
| Linen name | 13.39 |
| Share and QR glyphs | 13.76 |

**Every state passes** (`contrast-states.txt`). The tightest is the row sub-line on hover, at 4.63. Disabled Save is 3.15, which WCAG 1.4.3 exempts for inactive controls.

## Identifiers added / renamed
- **Tokens:** `--gold`, `--gold-deep`, `--cream`, `--black`, `--surface`, `--muted` (old meaning), `--line` and `--line-soft` are replaced by fin's names: `--sidebar`, `--background`, `--foreground`, `--card`, `--primary`, `--primary-foreground`, `--secondary`, `--muted`, `--muted-foreground`, `--accent`, `--border`, `--ring` and `--brand` (coral).
- **New tokens:** `--radius`, `--radius-md/lg/xl`, `--shadow-xs/lg/xl`, `--serif`, `--fast`.
- **Edit block:** `back.lineAccent` is new. `back.logo` and `footer.logo` now point to `brand/logo-linen.svg`.
- **QR markup:** `#qr` (`role="dialog"`) is now the panel `.qr-panel`, inside a new `#qr-layer` (`.qr`) with `#qr-overlay`. The sheet moved out of `.card` and is now a direct child of `<main>`. `.qr-heading` replaces the old `.eyebrow` on the sheet.
- **New CSS states/classes:**
  - `.back-line .accent`: the coral span, built from `lineAccent` with text nodes and no HTML.
  - `html.is-locked`: page scroll lock while the sheet is open.
- **QR SVG:** modules use `fill="currentColor"`, taken from `.qr-tile`'s `color: var(--background)`. The JavaScript has no colour literal now.

## Files
| Path | Change | Size |
|---|---|---|
| `index.html` | Rebuilt styles, the sheet's markup, the coral span, the overlay and scroll lock, the new words | 38 KB |
| `media/portrait.mp4` | Replaced by the kit copy: 1080², H.264, 24 fps, 120 frames, 5.0 s, silent, faststart | 1.0 MB |
| `media/poster.jpg` | Replaced by the kit copy (the clip's first frame) | 157 KB |
| `media/contact.jpg` | Replaced by the kit copy (480², same framing) | 40 KB |
| `brand/logo-linen.svg`, `brand/mark-linen.svg` | Added from the kit. Same paths as the old logos, linen `#E8E3DA` with coral lead `#F26A4B` | 25 KB |
| `favicon.png`, `apple-touch-icon.png` | Replaced by the kit copies (linen mark on `#141414`) | 15 KB |
| `fonts/inter.woff2`, `fonts/playfair-display.woff2` | Added: Latin variable fonts from `@fontsource-variable` 5.3.0, plus `OFL-inter.txt` and `OFL-playfair-display.txt` | 87 KB |
| `fonts/jetbrains-mono.woff2` | Unchanged. Byte-identical to `@fontsource-variable` 5.3.0 | 40 KB |
| `.vercelignore` | Now also ignores `Unit02_BUILD_NOTES.md`, `Unit01_verification/` and `Unit02_verification/` | — |
| `Unit02_verification/` | Before and after screenshots, state sheet, check outputs, sample vCard (not deployed) | 2.3 MB |
| **Removed** | `brand/logo-cream.svg`, `brand/logo-dark.svg`, `brand/mark-cream.svg`, `fonts/space-grotesk.woff2`, `fonts/OFL-space-grotesk.txt` | — |
| **Deleted, never committed** | `_rebrand-kit/` (after its files moved) | — |

Every kit file was **moved** into place, then checked by SHA-256 against the original. None was re-encoded or edited. The deployable folder is 1.5 MB. `fin-main.zip` and the 1440 master clip are not in the folder or the commit.

## How to preview
Same as Unit 01. From the build folder:
```
npx --yes serve -l tcp://0.0.0.0:4173
```
- Desktop: open http://localhost:4173.
- Phone, on the same Wi-Fi: open http://192.168.12.124:4173.

## Verification (builder)
The checks ran in headless Chrome against `http://192.168.12.124:4173/`, at 390 px (3× pixel density, touch) and 1440 px. Every check used a fresh profile with the cache off. Outputs are in `Unit02_verification/`.

| Check | Result |
|---|---|
| Hero plays muted, inline and looping; poster paints first | **Pass** at both widths. 1080×1080, 5.0 s. In the recorded run the poster loaded at 181 ms and playback started at 279 ms on the phone (933 / 985 ms on desktop, a slower load in that run; poster still first). |
| Runs past the restart cleanly | **Pass.** Frames were timed with `requestVideoFrameCallback` across the wrap: the last frame (4.958 s) leads straight into frame 0 with no skipped or repeated frame. Chrome takes 50–110 ms at the wrap against a normal 42 ms step, and the **old Unit 01 clip measured the same in the same run** (`loop-and-save-vs-unit01.json`), so that is the browser's loop, not the new clip. The clip's own seam (last frame to first) changes less than an average frame step in the middle of the clip, and no pixel moves more than 18/255. |
| Flip by tap and by keyboard; video pauses while flipped | **Pass:** tap, click, Enter and Space all flip. Focus moves to the other side's hint. The video pauses on the back and resumes on the front. |
| QR opens and closes, with focus handled | **Pass:** opens by tap, click or Enter. Closes by Esc, the close button (Enter) or the overlay. Focus goes to Close on open and back to the QR button on close. The page behind is inert and scroll-locked. |
| QR decodes to the page URL with a real reader (zxing-cpp) | **Pass.** `http://192.168.12.124:4173/` decodes from the phone and desktop screenshots, from both tile captures, and from each of those shrunk to ¼. |
| Share | **Pass.** Without a share sheet (desktop Chrome), it copies the link and shows "Link copied to clipboard." The share sheet itself needs HTTPS, as in Unit 01. |
| Save: a valid vCard with the new photo | **Pass.** Downloads `Nate Ivy.vcf`. vobject reads Nathan / Ivy, nickname Nate, NextSketch, the title, the work email and both URLs. There is no phone or address. Lines are CRLF and folded at 75 bytes. **The photo is a 480×480 JPEG, byte-identical to the new `media/contact.jpg`.** |
| Live Chicago time | **Pass.** It matches `America/Chicago` on reload. It still refreshes every 15 s, as in Unit 01, so one phone sample caught the minute turning over. |
| Zero outside requests | **Pass.** 11 requests, all to the page's own server. |
| Console errors or warnings | **None** at either width, with or without reduced motion. |
| Page weight, first visit, no cache | **1.37 MB** transferred (1,374,438 bytes), under the 3 MB budget. Reduced motion: **0.37 MB**, because the video never downloads. |
| Reduced motion | **Pass:** poster only, no video request, no entrance, and the flip is instant (0 s). Every transition is 0 s. |
| Contrast on every surface and state | **Pass.** See the Contrast section above. |
| Every component in every state against its fin reference | **Pass:** each was checked at rest, hover, active, focus-visible (reached with Tab) and disabled where it applies, with computed styles recorded. See `states/states-sheet.jpg` and `states.json`. Focus-visible draws the stone ring on all seven controls. |
| Grep sweep of everything that deploys | **Clean:** no gold, cream or old brown values (old hex or rgba), no `--gold`, no Space Grotesk, and no old logo files. The only hex values left are fin's dark set. The `rgb()` values left are fin's tokens with transparency (`input/30`, `primary/90` and similar), black shadows and the black overlay. |

## Differences from the brief (for Nate's review)
1. **The sheet now acts like fin's dialog, which brings two small new behaviours:**
   - Tapping the dimmed area outside the panel closes it.
   - The page can't scroll behind it.

   Both come with `dialog.tsx` (Radix does both), and a dimmed overlay that ignores taps feels broken on a phone. Opening, closing and focus behave exactly as they did in Unit 01.
2. **The Share and QR buttons no longer switch to dark-on-cream when flipped** (Unit 01, item 11). There's no cream side left to switch for.
3. **The entrance animation now holds its start state rather than its end state.** It used `forwards`, which pinned `opacity: 1` and stopped Save's disabled state from dimming. It now uses `backwards`, with the same 0.6 s and the same look.
4. **Save is 48 px tall, not fin's `lg` 40 px.** 40 px is under fin's own 44 px touch floor, and this is the card's main action. 48 px matches the site's "Start a Conversation" button.
5. **Save's disabled state can still be clicked.** Fin's disabled buttons ignore clicks (`pointer-events: none`). The card's only failure path shows a toast when you tap Save ("Could not download the contact card."), so Save keeps the 50% look but stays clickable to keep that behaviour.
6. **The 1440 master clip is 8.6 MB, not about 6 MB.** It stays out of the folder and the commit.
7. **The kit held `BRIEF_2026-10-15_card-rebrand.md`,** an earlier draft of this brief ("visual only; layout and behaviour stay exactly as they are"). I followed the brief Nate pasted (components rebuilt). The draft was deleted with the kit.
8. **`brand/mark-linen.svg` is kept, but the page doesn't reference it.** The kit table says to move it into place, replacing `mark-cream.svg` (which the page never referenced either; it was the icon source). It deploys as a 9.5 KB file nothing links to.
9. **The grep sweep covers the files that deploy.** `Unit01_BUILD_NOTES.md` is the Unit 01 record and still names Space Grotesk and the cream logos; I left it untouched. These notes name the removed files on purpose.
10. **`Unit01_verification/` doesn't exist in the repo,** although the Unit 01 notes refer to it. It is in `.vercelignore` now in case it comes back.
11. **The badges wrap onto two rows at 390 px,** as they did before (`before-phone-front.jpg`). The Unit 01 notes say the old badges fit on one row; at 390 px they didn't. The order is unchanged, and the words are Nate's.
12. **fin's own CSS comment puts coral at "6.6:1 on the dark card".** I measured 5.63 on `#1C1C1C` (6.09 on `#141414`). The brief's table is right.

## Open for Nate (judgment calls, each with a recommendation)
- **The flip-side body line on the site is Playfair italic in coral; on the card it is Inter in muted linen.** The brief puts coral only on "work in production", and coral mustn't spread. Italic would also need a fourth font file (about 40 KB). **Recommendation: keep it as built.** If you want it to match the site exactly, it's a small change: add the italic file and set the line in coral Playfair italic.
- **Dimmed-overlay tap closes the QR sheet** (difference 1). **Recommendation: keep.**
- **Unreferenced `brand/mark-linen.svg`** (difference 8). **Recommendation: keep it as the icon source.** The alternative is to add it to `.vercelignore` so it doesn't deploy.
- **G-gate on a real phone:** check the card on your iPhone. Headless Chrome can't show iOS's contact sheet, the real share sheet, or how Low Power Mode treats autoplay.

## Notes for the next unit
- Unit 01's P2 still applies: fill `phone` and set `quickActions`. The quick tiles are already styled to fin.
- Any new control should use the same set: the base `transition`, a `:focus-visible` ring entry, a `:active` state, hover inside `@media (hover: hover)`, and a 44 px size under `@media (pointer: coarse)`.
- If a new surface carries muted text, keep it off `--muted` (`#2A2A2A`); that pair fails at 4.18.
- `og:image` is still missing. It needs the deployed absolute URL (Unit 01, item 12).

## Dev-only tooling (not shipped; lives in the session scratchpad)
- `imageio-ffmpeg`: probing the clip, frame stepping, seam analysis.
- Pillow and numpy: contact sheets and pixel-level contrast over video.
- puppeteer-core with installed Chrome: screenshots, state driving, network, console and download checks.
- zxing-cpp: QR decoding.
- vobject: vCard parsing.
- `serve`: the local server, plus the untouched `main` build on port 4174 for the side-by-side loop and Save checks.
- Fonts from `@fontsource-variable/inter` and `@fontsource-variable/playfair-display` 5.3.0.

# Unit 03 — Build Notes: Digital Card, design system audit

**Brief:** Unit 03, Digital Card design system audit, 2026-10-15
**Built:** 2026-10-15
**Branch:** `audit-design-system`, cut from `main` at `f2bfaeb`, the Unit 02 merge (Nate merges)
**Build folder:** `C:\Users\nteiv\OneDrive\Documents\Projects\Digital Card_Nate`
**Status:** Audit done and fixes verified by the builder in headless Chrome at 390 px and 1440 px. Every check has a result. The card renders pixel-identical to Unit 02 in every captured state. Nine findings are waiting on Nate.

---

## What shipped
- **The audit:** all eleven checks have a result, the command behind it, and a pass, a fix or a finding (table below).
- **Thirteen invisible fixes**, mostly in `index.html`'s styles:
  - one token block at the top of the styles, under fin's names;
  - no colour, radius, type size or motion time written outside that block, except the documented exceptions;
  - one recipe each for buttons, mono labels and card surfaces;
  - one block for pressed states.
- **Nothing on screen moved.** 68 of 68 screenshots are pixel-identical before and after, at both widths and in every state. All 641,476 computed style values match too.
- **The card's standard is written down** (section near the end). That section is the rule for every future unit.
- **`_rebrand-kit/` is gone** from the folder. `brand/mark-linen.svg` no longer deploys.
- **Nine findings,** each with a recommendation. One is a real defect: the QR sheet's Close button misses the 44 px touch size (F1).

## Pre-flight
| Item | Result |
|---|---|
| Unit 02 merged to `main` | **Yes.** `origin/main` = `f2bfaeb` "Merge pull request #1 from Helios35/rebrand-zen-linen". `git diff 061bf75 origin/main` is empty, so it's the same tree as the Unit 02 branch. Local `main` was 2 behind and was fast-forwarded. |
| Clean tree on `main` | Clean, apart from the untracked `_rebrand-kit/`. |
| `_rebrand-kit/` | **It was back in the folder** (timestamp 12:18 today, after Unit 02 deleted it; probably OneDrive restoring it). It held one file, `BRIEF_2026-10-15_card-rebrand.md`, which is the Unit 02 brief. It was never tracked, so nothing could be committed. I moved it out of the folder to the session scratchpad rather than hard-deleting it. **Watch for OneDrive bringing it back a second time.** |
| Before-screenshots | Taken before any edit. `Unit03_verification/before/`. |

## The one place to edit
Unchanged: **the top of `index.html`, between `EDIT THIS CARD` and `END EDIT`.** No word changed and the edit block is byte-identical.

## The audit
The static checks (1–4, 9, 10) ran as `Unit03_verification/tools/audit.sh`. Each command is printed with its output in `checks/audit-before.txt` (a clean clone of `main`) and `checks/audit-after.txt` (this branch). The runtime checks (6–8, 11) ran in headless Chrome. The commands are listed under the table, as **C1**, **C2** and so on.

| # | Check | How I ran it | Before | Fix or finding | After |
|---|---|---|---|---|---|
| 1 | One token block | **C1**: count `:root` blocks, find custom properties declared outside it, grep motion times, easing curves, font families, sizes, radii and shadows outside its line range | One `:root`, but four motion times (`.6s`, `.7s`, `.4s`, `.09s`) and one easing curve were written in rules. Font tokens used non-fin names (`--sans`, `--serif`, `--mono`). | **Fix X1, X2** | **Pass.** The `:root` block is the first thing in `<style>`. Outside it, the only `font-family` literals are the three `@font-face` declarations that name the files. The only time written is `0s` (an instant swap, see the standard). |
| 2 | No loose values | **C2**: grep hex and `rgb()/hsl()/color-mix()` outside the block, a comment-stripped scan for all 148 CSS named colours, `theme-color`, every `style=` attribute, colour literals in the script, the decoded grain SVG, every deploying SVG file | 9 `rgb()` in rules: 7 were fin opacity steps, 2 were uncommented black transparencies. One hex in `theme-color`. Hex fills in the two brand SVGs. Script, QR fill and named colours were clean, and the grain SVG declares no colour. | **Fix X3, X7.** **Findings F2, F3** | **Pass with two findings.** The only `rgb()` left outside the block are the two black transparencies, each commented. `theme-color` (F2) and the SVG fills (F3) are the open items. |
| 3 | No old tokens | **C3**: grep `--gold`, `--gold-deep`, `--cream`, `--black`, `--surface`, `--line`, `--line-soft`, Space Grotesk and the old logo names across everything that deploys; list `fonts/` and `brand/` | Clean | — | **Pass.** All greps empty. Only the Unit 01 and 02 notes name them, as history. |
| 4 | Fin's scales only | **C4**: list every `--radius*`, `border-radius`, `--shadow-*`, `box-shadow`, `font-family`, `font-size` and `font-weight` | Radius came from fin's scale except the badge's `999px`. The shadow tokens match fin's `globals.css` byte for byte. The name's `text-shadow` isn't on fin's scale. Families were Inter, Playfair and JetBrains Mono only. Seven size steps were written as literals: 11, 12, 14, 16, 24, 27, 38 px. | **Fix X5, X6.** **Findings F4, F5** | **Pass with two findings.** Every radius, shadow, family and size reads a token. 27 px and 38 px are off fin's token-layer steps (F5). |
| 5 | One recipe per component | Read every rule against `button.tsx`, `dialog.tsx` and Unit 02's component table. **C5**: `dead.py` lists every class and token. | Per-button copies: `radius-md` four times and the 16 px icon size three times; only the icon buttons had a disabled rule. The mono-label recipe was written five times and the card-surface recipe twice. Pressed states were declared twice for four controls. | **Fix X8–X11.** **Finding F6** | **Pass.** Every button is `.btn` plus one variant. There is one label recipe, one card surface and one pressed-state block. Each component matches Unit 02's record. F6 lists three small differences from fin's literal class strings. |
| 6 | Every state | **C6**: `capture.js` takes real keyboard focus (Tab) on every control, CDP-forced `:hover` and `:active`, and disabled; screenshots plus computed styles. States sheets are in `before/` and `after/`. | Every control has hover (pointer devices only), active and focus-visible. Disabled was on the icon buttons and Save. Focus is never removed: `outline: none` always comes with fin's 3 px ring, plus a forced-colors outline. **On touch, Close renders 28 px, not 44 px.** Pressed quick tiles don't lift their border the way link rows do. | **Fix X8** (disabled now on every button, per fin). **Findings F1, F8** | **Pass with two findings.** The flip surface itself is a pointer shortcut; the "Tap" hint is its keyboard path and carries every state. |
| 7 | Motion | **C7**: grep the transition and animation times; read every computed `transition-duration`, `transition-delay` and `animation-name` under `prefers-reduced-motion: reduce` | Every hover and state change is 150 ms. The flip (0.7 s) and the entrance (0.6 s) are exempt. The poster-to-video fade is 0.4 s. Reduced motion: every duration and delay is `0s`, no animation, no video request. | **Fix X2** (all times now tokens). **Finding F9** | **Pass.** The fade is a one-time media fade, not a state change (F9 asks Nate to confirm it as exempt). |
| 8 | Contrast | **C8**: `contrast.js`, WCAG 2 formula against the pixels painted behind each piece of text or mark. Text is hidden first and the worst pixel counts. Both widths; rest, hover, active and focus on every control; 40 frames across the clip plus the poster. | 1,697 measurements, **0 failures** | — | **Pass.** 1,697 measurements, 0 failures, and **every ratio identical before and after.** The tightest values are under Contrast below. |
| 9 | Edit block intact | **C9**: grep below `END EDIT` for `aria-label`, `alt`, `title`, quoted phrases, locales, and text nodes in the markup | Every on-screen word, the `<title>` and the `<meta>` tags live in the block. **Hardcoded below `END EDIT`:** four screen-reader labels, the phrase " to flip the card", the time locale `"en-US"`, and `lang="en"`. | **Finding F7** | **Finding open.** Moving them would add fields to the edit block, which is Nate's call. |
| 10 | Nothing dead | **C10**: `dead.py` (classes, tokens, ids, keyframes, script names), plus every file that deploys (tracked, minus `.vercelignore`) that the page never references | 51 classes, 25 tokens, 36 ids, 1 keyframe and every script name were all used. **`brand/mark-linen.svg` deployed but was referenced nowhere.** The three OFL licence files deploy unreferenced on purpose (the font licences require them). | **Fix X12** | **Pass.** 52 classes and 47 tokens, all used. Dormant by design, not dead: the quick-tile CSS and the `phone`, `mail`, `instagram`, `x`, `youtube` and `tiktok` icons, which are the edit block's documented options. |
| 11 | Budgets | **C11**: `behaviour.js` on a fresh profile with the cache off: every request, transferred bytes, console messages and page errors | 11 requests, all same-origin; 1,374,766 bytes; no console output | — | **Pass.** 11 requests, **0 outside**, **1,375,995 bytes (1.38 MB)**, up 1,229 bytes from the longer token block and its comments. No console messages or errors. Reduced motion: 370,178 bytes. |

### The commands
- **C1** (excerpt; the full set is `audit.sh` CHECK 1):
  ```
  grep -c '^  :root {' index.html
  awk -v a=$T0 -v b=$T1 'NR<a || NR>b' index.html | grep -nE '(transition|animation)[^;]*[^0-9](\.[0-9]+|[1-9][0-9]*)m?s\b'
  awk -v a=$T0 -v b=$T1 'NR<a || NR>b' index.html | grep -E 'cubic-bezier'
  awk -v a=$T0 -v b=$T1 'NR<a || NR>b' index.html | grep -E 'border-radius:' | grep -v 'border-radius: *var(--'
  ```
  `$T0`/`$T1` are the `:root` block's first and last lines (`grep -n '^  :root {'` and the next `^  }$`).
- **C2:**
  ```
  awk -v a=$T0 -v b=$T1 'NR<a || NR>b' index.html | grep -nE '#[0-9a-fA-F]{3,8}\b'          # ids filtered out
  awk -v a=$T0 -v b=$T1 'NR<a || NR>b' index.html | grep -nE '(rgba?|hsla?|hwb|lab|lch|oklab|oklch|color-mix)\('
  python -I tools/named_colours.py index.html $T0 $T1
  grep -oE 'base64,[A-Za-z0-9+/=]+' index.html | cut -d, -f2 | base64 -d
  grep -oiE '#[0-9a-f]{3,8}\b|rgba?\([^)]*\)' brand/*.svg | sort | uniq -c
  ```
- **C3:**
  ```
  grep -nE -- '--(gold|gold-deep|cream|black|surface|line|line-soft)\b' index.html brand/*.svg
  grep -rniE 'space.?grotesk' . --exclude-dir=.git --exclude-dir=.claude --exclude-dir=Unit02_verification --exclude='Unit0*_BUILD_NOTES.md'
  grep -rnE 'logo-cream|logo-dark|mark-cream' .  (same exclusions)
  ```
- **C4:**
  ```
  grep -noE 'border-radius: *[^;]+' index.html
  grep -noE 'box-shadow: *[^;]+' index.html
  grep -oE 'font-size: *[^;]+' index.html | sort | uniq -c
  ```
- **C5, C10:** `python -I tools/dead.py index.html` and
  ```
  comm -23 <(git ls-files | sort) <(git ls-files -ci --exclude-from=.vercelignore | sort) | while read f; do grep -qF "$(basename "$f")" index.html || echo "$f"; done
  ```
- **C6:** `node tools/capture.js <url> <out>`, then `python -I tools/compare.py before after report.json`.
- **C7:** `capture.js` reads every element's computed `transition-duration`, `transition-delay` and `animation-name` under emulated `prefers-reduced-motion: reduce` (`checks/capture-*.json`, `reduced`).
- **C8:** `node tools/contrast.js <url> <out>` writes `checks/contrast-before.txt` and `checks/contrast-after.txt`.
- **C9:**
  ```
  awk -v e=$END 'NR>e' index.html | grep -nE 'aria-label="[^"]+"|alt="[^"]+"|title="[^"]+"'
  awk -v e=$END 'NR>e' index.html | grep -nE '"[A-Z][a-z]+( [a-z]+)+"|" to [a-z]+|en-US|lang='
  ```
- **C11:** `node tools/behaviour.js <url> <out>` (CDP `Network.loadingFinished` byte totals, every request URL, console and page errors).

## Fixes (each one is invisible)
"Invisible" is measured. A deterministic harness froze the clock at 3:42 PM Chicago and paused the clip at 1.0 s. A control run of the unchanged card against itself came out 68/68 pixel-identical, so the harness itself introduces no differences. The same harness on this branch then gave **68/68 screenshots pixel-identical** (34 per width: page states, focus on every control, hover, active, disabled) and **62/62 computed-style dumps identical: 641,476 values**, with custom properties excluded because those names were what changed. Report: `checks/compare-before-after.json`.

| # | Fix | Why it's invisible |
|---|---|---|
| X1 | **Token block moved to the top of `<style>`**, above `@font-face`. Font tokens renamed to fin's names: `--sans`, `--serif` and `--mono` are now `--font-sans`, `--font-serif` and `--font-mono` (as in `zen-linen-fin.css`). `--fast` is now `--duration-fast` and `--ease` is now `--ease-flip`. | Declaration order between `:root` and `@font-face` has no effect, and a rename changes no value. |
| X2 | **Every motion time is a token:** `--duration-flip` 0.7 s, `--duration-entrance` 0.6 s, `--duration-fade` 0.4 s, `--delay-face-swap` 0.09 s and `--ease-entrance`. | Each token holds exactly the literal it replaced, so the computed values are unchanged. |
| X3 | **The seven fin opacity steps in rules became tokens holding the same values:** `--input-30`, `--input-50`, `--accent-50`, `--primary-90`, `--primary-80`, `--background-0`, `--background-60` and `--background-90`. | Same `rgb()` value, moved into the block. They're written as `rgb()` rather than `color-mix()` on purpose, because `color-mix()` would leave the hero shade unpainted on iOS before 16.2. |
| X4 | **Added `--input`** (`#2C2C2C`, fin's `dark:border-input`). The outline buttons' border now reads it, as fin and Unit 02's notes say, instead of `--border`. | `--input` and `--border` are the same value in fin's dark set. |
| X5 | **Badge `999px` became `--radius-full`** (fin's `rounded-full`). | Same value. |
| X6 | **Type sizes are tokens:** `--text-eyebrow` 11 (fin's own name), `--text-xs` 12, `--text-sm` 14, `--text-base` 16, `--text-2xl` 24, `--text-display-sm` 27 and `--text-display` 38. | Same px values. They stay px, because rem would change size for anyone with a non-default browser font size. |
| X7 | **The two black transparencies are commented in place:** the QR overlay (fin's `black/50`) and the name's legibility shadow. | Comments only. |
| X8 | **Button recipe.** Every button now carries `.btn`: Share, QR, both "Tap" hints, Save and Close. `.btn` holds `radius-md`, the 16 px icon size and the disabled state. The variants are `.save` (primary), `.icon-btn` (outline, icon size), `.flip-hint` (ghost) and `.qr-close` (dialog close). This removed four radius copies, three icon-size copies and the icon-only disabled rule. | The same declarations now come from one rule. The disabled state now also covers the "Tap" hints and Close, but no button is ever disabled on the card, so nothing renders differently. The harness also forced Share to `disabled` and it rendered identically. |
| X9 | **One label recipe** (`.eyebrow, .flip-hint, .badge, .divider, .qr-heading`: mono, `--text-eyebrow`, 500, 0.12 em, uppercase) replaces five copies. | Identical declarations, and no later rule overrides them. |
| X10 | **One card-surface recipe** (`.link, .quick a`) replaces two copies. | Identical declarations. |
| X11 | **States reordered:** hover → active → focus-visible → touch floor. Every `:active` rule is now in one block after hover, which removed four `:active` re-declarations inside the hover block. | Specificity and order were checked rule by rule, property by property, and every combination still resolves the same way: hover+active, active+focus, and touch with no hover. The computed-style diff confirms it in every captured state. |
| X12 | **`.vercelignore`:** `brand/mark-linen.svg` no longer deploys, which settles Unit 02's open question with its own alternative. The file stays in the repo as the icon source. The Unit 03 notes and evidence folder are also ignored. | The page never loaded `mark-linen.svg`. |
| X13 | **`_rebrand-kit/` removed** from the folder (untracked, never deployed). | Not part of the site. |

## Findings (not fixed; each has a recommendation)
| # | Finding | Why not fixed here | Recommendation |
|---|---|---|---|
| **F1** | **QR Close misses the 44 px touch floor.** On touch it renders 28 × 28 px, measured in `checks/capture-*.json` and the style dumps. Unit 02's notes and fin (`dialog.tsx` `pointer-coarse:size-11`, UX_SPEC §9.6) say 44 px. Cause: the `.qr-close` rule (`index.html:433`) comes after the `@media (pointer: coarse)` block, has the same specificity, so it wins. | At rest the box is invisible and the glyph's centre stays 30 px from the corner either way. But the pressed fill, the focus ring and the hit area would all grow on phones, which is a visible change. | **Fix it in a follow-up:** move the touch-floor block below the QR sheet and toast rules, so it sits just above reduced motion. It's a one-block move. Verify with the same harness: the only expected difference is Close on the phone in its active and focus states. **I recommend doing this one.** It's a real miss against the touch floor, on the one control a phone user must hit first time. |
| **F2** | **`theme-color` is a hex literal** (`<meta name="theme-color" content="#101010">`, in the edit block). | HTML attributes can't read CSS custom properties. Setting the colour from script would leave the browser bar uncoloured until the script runs. | **Keep the literal and record it as the standard's one HTML exception:** it must equal `--sidebar`. The token's comment now says so. |
| **F3** | **The brand SVG files carry hex fills:** `logo-linen.svg` and `mark-linen.svg` use `#E8E3DA` and `#F26A4B`. | They load as `<img>`, which is an isolated document that can't read the page's tokens. They're kit assets kept byte for byte, and the values equal `--foreground` and `--brand` exactly. | **Accept them as an asset exception.** If a token ever changes, the logos are re-exported from the kit. Inlining the SVG to use `currentColor` isn't worth it: the logo is 16 KB, most of it provenance metadata. |
| **F4** | **The name's `text-shadow`** (`0 2px 18px`, 50% black) is not on fin's shadow scale. | It does legibility over the video (it dates from Unit 01), not elevation. Fin's 3–9% steps can't do that job, and removing it changes the hero. | **Keep it as the one allowed text-shadow.** It's now commented in place and recorded in the standard. |
| **F5** | **Two type sizes, 27 px (flip-side line) and 38 px (name), are off fin's token-layer steps** (Tailwind's 24, 30, 36, 48). | They're Unit 02's deliberate calls, matched to the site, and changing them is a visual change. | **Keep them.** They're now named tokens (`--text-display-sm`, `--text-display`), so they can't drift. |
| **F6** | **Three small differences from fin's literal class strings.** Each matches Unit 02's record. (a) Outline and ghost buttons keep linen text on hover; fin's variants switch to `--accent-foreground` (stone `#D1CFC0`). (b) Save's label is 16 px; fin's buttons are `text-sm` (14 px). (c) The "Tap" hint's icon is 14 px; fin's button icons are 16 px (12 px at `xs`). | All three are visible changes. | **Keep (b) and (c):** Save is the card's main action, and a 14 px icon sits right with the 11 px label. **(a) is the only one worth considering** if you want strict fin: on hover, the Share and QR glyphs and the "Tap" text would tint from linen to stone. My recommendation is to keep linen. |
| **F7** | **Screen-reader words are hardcoded below `END EDIT`:** `aria-label` "Share" (`:468`), "Show QR code" (`:471`) and "Close" (`:531`); "QR code linking to this page" (`:733`); the " to flip the card" suffix (`:583`); the time locale `"en-US"` (`:643`); and `lang="en"` (`:2`). | Unit 01's rule covered on-screen words, and these aren't on screen. Moving them adds fields to the edit block, which changes its shape and is Nate's call. No word would change. | **Move them in a small follow-up:** `labels.share`, `labels.showQr`, `labels.close`, `labels.qrImage` and `labels.flipHint` ("Tap to flip the card"), plus `locale: "en-US"` (also used for `lang`). Same words, nothing visible. The next person's card would then be fully editable in one place. |
| **F8** | **Quick-action tiles (off until P2) don't lift their border to `--accent` when pressed on touch;** link rows do. The CSS said "same states as the link rows". | The tiles don't render today, so the change can't be verified visually now. | **When P2 turns them on,** change `.link:active { border-color: var(--accent); }` (`:393`) to `.link:active, .quick a:active`. |
| **F9** | **The poster-to-video fade is 0.4 s.** The brief exempts the flip, the entrance and the loop, and §8's ceiling is 200 ms. | It's a one-time media fade, not a hover or state change. Shortening it would change how the video appears. | **Treat it as exempt along with the loop.** The standard records it that way. |

Known and unchanged from Unit 02: Save's disabled look (`:not([href])`) stays clickable so its failure toast can show (Unit 02, difference 5). Disabled Save measures 3.15:1, which WCAG 1.4.3 exempts for inactive controls.

## Contrast (measured, both runs identical)
The full tables are in `checks/contrast-after.txt`: 1,697 measurements, 0 failures. Each ratio is against the worst pixel behind the text, with the text hidden (shadows off, which is conservative).

| Where | Worst ratio | Need |
|---|---|---|
| Link sub-line on hover (`--muted-foreground` on `--secondary`) | **4.63** | 4.5 |
| Link icon, pressed (coral on `--muted`) | 4.74 | 3 |
| Muted text and marks on `--card` (sub-lines, arrows, flip-side body, "Tap to flip back") | 4.96 | 4.5 / 3 |
| Coral "Chicago · time" over the video (40 frames + poster, both widths) | **5.25** | 4.5 |
| Muted "Tap" label / icon over the video | 5.30 / 5.26 | 4.5 / 3 |
| Linen name over the video | 13.33 | 4.5 |
| Share and QR glyphs over the video, rest / hover / pressed | 13.89 / 13.16 / 11.23 | 3 |
| Focus ring (stone) against what's around it, worst anywhere (the back's hint on `--card`); over the video | 10.64; 11.04 | 3 |
| QR modules on the linen tile | 14.41 | 3 |
| Close glyph at 70% on the sheet | 7.50 | 3 |

## The card's standard going forward
**This is the rule for every future unit.** A change that's meant to be invisible proves it with the harness in `Unit03_verification/tools/`. Capture before and after with `capture.js` and run `compare.py`: zero differing pixels and zero differing properties.

### 1. The token block
Every colour, radius, shadow, font, type size and motion time is declared here, once, at the top of `<style>`. Nothing below it writes a value; rules read `var()`. This is the block as it stands:

```css
  :root {
    color-scheme: dark;

    /* Colour: fin's dark set (zen-linen-fin.css, .dark). These are the card's only colours. */
    --sidebar: #101010;            /* fin's darkest step: the page behind the card (theme-color mirrors it) */
    --background: #141414;         /* the card itself, and the QR sheet */
    --foreground: #E8E3DA;         /* linen */
    --card: #1C1C1C;               /* surfaces on the card: link rows, flip panel, toast */
    --primary: #D1CFC0;            /* stone */
    --primary-foreground: #363636;
    --secondary: #222222;
    --muted: #2A2A2A;
    --muted-foreground: #8E8A83;
    --accent: #363636;
    --border: #2C2C2C;
    --input: #2C2C2C;              /* the outline button's border (fin's dark:border-input) */
    --ring: #D1CFC0;
    --brand: #F26A4B;              /* coral: the one accent */

    /* Fin's opacity steps (Tailwind's token/NN): each is its base token above at that alpha.
       Written out as rgb() so they paint on every browser. Change one with its base. */
    --input-30: rgb(44 44 44 / 0.3);        /* --input /30: outline button at rest */
    --input-50: rgb(44 44 44 / 0.5);        /* --input /50: outline button, hover */
    --accent-50: rgb(54 54 54 / 0.5);       /* --accent /50: ghost button, hover */
    --primary-90: rgb(209 207 192 / 0.9);   /* --primary /90: primary button, hover */
    --primary-80: rgb(209 207 192 / 0.8);   /* --primary /80: primary button, pressed */
    --background-0: rgb(20 20 20 / 0);      /* --background /0, /60, /90: the hero shade, */
    --background-60: rgb(20 20 20 / 0.6);   /* where the clip fades into the card under the name */
    --background-90: rgb(20 20 20 / 0.9);

    /* Radius: fin's scale, every step derived from one --radius (app/globals.css). */
    --radius: 0.5rem;
    --radius-md: calc(var(--radius) * 0.8);
    --radius-lg: var(--radius);
    --radius-xl: calc(var(--radius) * 1.4);
    --radius-full: 999px;          /* fin's rounded-full (a pill): the one step not derived, as in fin */

    /* Shadow: fin's soft scale. Near-invisible in dark on purpose: the border separates. */
    --shadow-xs: 0 1px 4px 1px rgb(0 0 0 / 0.04);
    --shadow-lg: 0 8px 30px 5px rgb(0 0 0 / 0.06);
    --shadow-xl: 0 14px 44px 7px rgb(0 0 0 / 0.07);

    /* Type: fin's three families (zen-linen-fin.css names), then the size steps. Fin's theme
       sets no size scale (UX_SPEC §1): these are its token layer's steps (Tailwind's text-*
       and fin's own --text-eyebrow) plus the card's two display sizes. */
    --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    --font-serif: "Playfair Display", Georgia, "Times New Roman", serif;
    --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    --text-eyebrow: 11px;          /* fin's one sub-12px step: every mono label, the footer line */
    --text-xs: 12px;
    --text-sm: 14px;
    --text-base: 16px;
    --text-2xl: 24px;
    --text-display-sm: 27px;       /* the flip-side line */
    --text-display: 38px;          /* the name */

    /* Motion. Every state change runs --duration-fast (fin §8: under 200ms). The flip, the
       entrance and the poster-to-video fade keep Unit 01's timing, exempt from that ceiling. */
    --duration-fast: 150ms;
    --duration-flip: 0.7s;
    --duration-entrance: 0.6s;
    --duration-fade: 0.4s;
    --delay-face-swap: 0.09s;      /* the faces swap visibility at the flip's edge-on point */
    --ease-flip: cubic-bezier(.22, 1, .36, 1);
    --ease-entrance: cubic-bezier(.2, .7, .2, 1);
  }
```

**Allowed outside the block, and nothing else:**
- a black transparency for an overlay or a shadow, with a comment on the same line (today: the QR overlay and the name's shadow);
- the keywords `transparent`, `currentColor` and `none`, which have no colour of their own;
- `0s` for an instant swap (visibility at the flip's edge-on point, and the QR sheet's hide);
- `theme-color` (F2), which must equal `--sidebar`;
- the brand SVG files' own fills (F3).

**Adding a colour** means adding it to fin first. The card uses fin's dark set and nothing else (UX_SPEC §1 and §9.2). An opacity step is written as `--<token>-<NN>`, right under its base token.

### 2. The component recipes
| Component | Markup | Recipe | States | Fin reference |
|---|---|---|---|---|
| **Interactive base** | `.btn`, `.link`, `.quick a` | `cursor: pointer`, `outline: none`, `touch-action: manipulation`, colour/background/border/opacity transitions at `--duration-fast` | — | `components/shell/interaction.ts` (via `button.tsx`) |
| **Button base** | `.btn` (every button) | `--radius-md`, 16 px icons | disabled: 50%, no pointer | `button.tsx` base |
| Primary (Save) | `.btn.save` | `--primary` fill, `--primary-foreground` text, `--text-base` 500, 48 px tall, 8 px gap, 0 24 px padding | hover `--primary-90`; pressed `--primary-80`; focus: 2 px `--background` gap then a 3 px ring; disabled `:not([href])` at 50%, still clickable | `default` variant |
| Outline icon (Share, QR) | `.btn.icon-btn` | 36 px square (44 on touch), `--input` border, `--input-30` fill, `--foreground` glyph, `--shadow-xs` | hover `--input-50`; pressed `--muted`; focus ring + `--ring` border | `outline`, size `icon` |
| Ghost ("Tap" hint) | `.btn.flip-hint` + label | 32 px tall (44 on touch), 0 10 px padding (0 14 on touch), transparent border, `--muted-foreground`, 14 px icon | hover `--accent-50` + `--foreground`; pressed `--accent` + `--foreground`; focus ring + border | `ghost`, size `sm` |
| Dialog close | `.btn.qr-close` | 28 px (44 on touch, once F1 is fixed), transparent border, `--foreground` at 70% | hover, focus and pressed raise it to 100%; pressed adds `--muted` | `dialog.tsx` close |
| **Label** | `.eyebrow`, `.flip-hint`, `.badge`, `.divider`, `.qr-heading` | `--font-mono`, `--text-eyebrow`, 500, 0.12 em, uppercase; colour set per use | — | `--text-eyebrow` (`globals.css`) |
| **Card surface** | `.link`, `.quick a` | `--card` fill, `--border` hairline, `--radius-lg`, `--foreground` | hover `--secondary` + `--accent` border; pressed `--muted` (rows also take the `--accent` border and lift their sub-line and arrow to `--foreground`); focus ring + border | fin card |
| Badge | `.badge` + label | `--secondary` fill, `--border` hairline, `--radius-full`, a 6 px coral diamond | not interactive | none (extended) |
| Dialog (QR sheet) | `.qr` > `.qr-overlay` + `.qr-panel` | black/50 overlay; panel in `--background` with `--border`, `--radius-lg`, `--shadow-lg`, 24 px padding; fades and scales from 95% in `--duration-fast` | Esc, Close or the overlay closes it; focus moves to Close and returns to the QR button | `dialog.tsx` |
| QR tile | `.qr-tile` | `--foreground` tile, `--background` modules (`currentColor`), `--radius-md`, 14 px padding | — | scan floor |
| Toast | `.toast` | `--card`, `--border`, `--radius-lg`, `--shadow-lg`, `--text-sm`, `--duration-fast` in and out | — | fin card surface |
| Hero frame | `.card` | `--background`, `--border`, `--radius-xl`, `--shadow-xl` | — | fin radius scale and border rule |
| Flip panel | `.face-back` | `--card`, `--border` bottom hairline | — | fin card surface |
| Focus ring | `:focus-visible` | 3 px `--ring` box-shadow, plus `--ring` border on bordered controls; forced-colors outline 2 px | never removed | `button.tsx` focus |

### 3. Rules for any new or changed control
1. **A new button is `class="btn <variant>"`.** It gets the interactive base, the radius, the icon size and disabled for free.
2. **States go in the state blocks, in this order:** hover (inside `@media (hover: hover)`, so it never sticks after a tap) → active (everywhere) → focus-visible (add the control to the border-ring list if it has a border) → touch floor (`@media (pointer: coarse)`, 44 px, 8 px apart). **Component rules go above the state blocks.** The QR sheet sitting below them is the cause of F1.
3. **Motion:** state changes use `--duration-fast`, and nothing new goes over 200 ms. The flip, entrance, poster fade and loop keep Unit 01's timing. The reduced-motion block stays last and removes everything.
4. **Type:** families come from `--font-*` and sizes from `--text-*`. A mono label joins the label recipe and doesn't copy it.
5. **Contrast:** measure every new pair with a tool, in every state and over the video. Muted text never goes on `--muted` (4.18:1).
6. **Words:** they live in the edit block. Screen-reader words follow once F7 is done.

## Files
| Path | Change | Size |
|---|---|---|
| `index.html` | Token block, recipes and state order (X1–X11). The edit block, the markup's words and the script's behaviour are unchanged. The only markup change is six `class` attributes gaining `btn`. | 41.8 KB on disk (was 38.9 KB); +1,229 bytes transferred |
| `.vercelignore` | Adds `Unit03_BUILD_NOTES.md`, `Unit03_verification/` and `brand/mark-linen.svg` | — |
| `Unit03_BUILD_NOTES.md` | This file (not deployed) | — |
| `Unit03_verification/` | `before/` and `after/` screenshots (page states and a states sheet per width), `checks/` (the audit, compare, contrast, behaviour, QR and vCard outputs), and `tools/` (the harness). Not deployed. | 2.1 MB |
| **Removed from the folder** | `_rebrand-kit/` (untracked; moved to the session scratchpad) | — |

## How to preview
Same as before. From the build folder:
```
npx --yes serve -l tcp://0.0.0.0:4173
```
- Desktop: http://localhost:4173.
- Phone, on the same Wi-Fi: http://192.168.12.124:4173.

## Verification (builder)
The checks ran in headless Chrome 154 against the session's local server, at 390 px (3× density, touch, no hover) and 1440 px. Port 4173 was held by another session's `serve`, so my server ran on `http://localhost:61045/`, and that is the URL the QR encodes in these runs. Every run used a fresh profile with the cache off. Outputs are in `Unit03_verification/checks/`.

| Check | Result |
|---|---|
| Harness is deterministic (unchanged card against itself) | **68/68** screenshots and **62/62** style dumps identical (`compare-control-run.json`) |
| After matches before, in every state | **68/68 pixel-identical, 641,476 computed values identical** (`compare-before-after.json`). States: front, flipped, the QR sheet (full page and viewport), the QR tile, the Share toast, the Save toast, reduced motion, focus on all eight controls (by Tab), hover and active on all eight, and disabled Save and Share. Both widths. |
| Flip | **Pass, same as before.** Tap (phone), click, Enter and Space all flip. The video pauses on the back and plays on the front. The faces swap `inert`. Keyboard focus moves to the other side's hint. |
| QR sheet | **Pass.** Opens by click and by Enter. Closes by Esc, by the Close button and by the overlay. Focus goes to Close, then back to the QR button. The page behind is inert and doesn't scroll (scrollY stayed 0 under a 400 px wheel). |
| QR decodes with a real reader (zxing-cpp) | **12/12:** the tile, the viewport and full-page captures, at full size and ¼, at both widths, all decode to the page URL. |
| Share | **Pass.** With a share sheet, the card hands over `{title: "Nate Ivy", text: "Nate Ivy — Lead Product Architect & CEO, NextSketch", url}`; the sheet was stubbed so the call could be recorded. Without one, it copies the link (the clipboard read back the URL) and shows "Link copied to clipboard." |
| Save: a valid vCard with photo | **Pass.** Downloads `Nate Ivy.vcf`. vobject reads Nathan / Ivy, the nickname Nate, NextSketch, the title, the work email and both URLs. There's no TEL and no ADR. Lines are CRLF and at most 75 bytes. **The photo is a 480 × 480 JPEG, byte-identical to `media/contact.jpg`.** The parse results are identical before and after. |
| Links | **Pass.** Website and LinkedIn: the hrefs equal the edit block's URLs, with `target=_blank` and `rel=noopener`. |
| Live time | **Pass.** It matches `America/Chicago` now (1:43 PM in the after run). |
| Tab order | Share → QR → Tap → Save → Website → LinkedIn, unchanged. |
| Budgets | 11 requests, 0 outside; 1.38 MB; no console messages or errors. Reduced motion: no video request, 0.37 MB. |

## Open for Nate
- **F1, the QR Close touch size:** approve the one-block move as a follow-up. This is the one I'd do.
- **F7, the screen-reader words:** approve moving them into the edit block. Same words, new fields.
- **F2 and F3 (exceptions), F4, F5, F6, F9 (keep as built):** confirm. F6(a), the stone hover text, is the only one where strict fin would change the look.
- **`_rebrand-kit/`** keeps coming back (probably OneDrive). If it reappears, it's safe to delete. Nothing references it, and it was never tracked.
- **Still open from Unit 02:** check the card on your iPhone (the share sheet, the contact sheet, Low Power Mode). Nothing in this unit changes that.

## Dev-only tooling (not shipped)
These live in the session scratchpad, with copies of the scripts in `Unit03_verification/tools/`:
- puppeteer-core 24 driving the installed Chrome: captures, forced states, network, console and downloads;
- pngjs: pixel reads for contrast;
- Pillow and numpy: pixel comparison and evidence sheets;
- zxing-cpp: QR decoding;
- vobject: vCard parsing.

To re-run the harness, put `puppeteer-core` and `pngjs` in a scratch folder (not this one) and point the scripts at a running `serve`. `apply_fixes.py` is the exact transformation applied to `index.html`: 29 exact-match replacements, each asserted to match once.

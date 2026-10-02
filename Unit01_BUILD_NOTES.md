# Unit 01 — Build Notes: Digital Card Site

**Brief:** `claude_BRIEF_2026-10-02_digital-card-site.md`
**Built:** 2026-10-02
**Build folder:** `C:\Users\nteiv\OneDrive\Documents\Projects\Digital Card_Nate`
**Status:** Built and verified by the builder. Waiting on Nate for G2.

---

## What shipped
A single static page with the reference card's layout and moves, in Next Sketch colors and fonts:
- Hero: your looping portrait clip with the name over it, live Chicago time, Share and QR buttons, and a tap-to-flip back panel.
- Below the hero: role line, two badges, the Save button, the link list, and the footer.
- No build step, no server code and no outside requests. The folder deploys as it is.

## The one place to edit
**The top of `index.html`, between `EDIT THIS CARD` and `END EDIT`.** It contains:
- The page title and link-preview text.
- The icon links.
- A `window.CARD = {…}` object holding name, title, company, place and time zone, role line, badges, the back-of-flip words, links, phone and email (empty for now), quick actions, footer, media paths, share text and every on-screen label.

Nothing below `END EDIT` needs to change for the next person. Their card is that block plus new files in `media/` (and in `brand/` if it's a different company).

**P2 (phone):** fill in `phone`. It goes into the saved contact; to also show Call/Email buttons on the card, set `quickActions: ["call", "email"]`. No other changes are needed.

**Email** is already set (`nate@nextsketch.com`). It is in the saved contact only; no Email button shows on the card because `quickActions` is empty.

## Files
| Path | What | Size |
|---|---|---|
| `index.html` | Page, styles, behavior, and the edit block | 31 KB |
| `media/portrait.mp4` | Web copy of `assets/portrait-master.mp4`: 1080×1080 H.264, 5.0 s, silent | 699 KB |
| `media/poster.jpg` | `assets/portrait-poster.jpg`, unchanged | 133 KB |
| `media/contact.jpg` | 480×480 head-and-shoulders crop of the poster, used as the saved contact's photo | 18 KB |
| `brand/logo-dark.svg`, `logo-cream.svg`, `mark-cream.svg` | Supplied logos, unchanged | 41 KB |
| `fonts/space-grotesk.woff2`, `jetbrains-mono.woff2` | Latin variable fonts stored in the folder, plus their OFL licence files | 61 KB |
| `vendor/qrcode.js` | QR generator (qrcode-generator 2.0.4, MIT, licence in the file header), unmodified | 55 KB |
| `favicon.png`, `apple-touch-icon.png` | `mark-cream.svg` on brand black | 3 KB |
| `.vercelignore` | Keeps `.claude/` and these notes out of a Vercel deploy | — |

The folder holds 1.03 MB in total.

## How to preview
**On the desktop:** from the build folder, run:
```
npx --yes serve -l tcp://0.0.0.0:4173
```
Then open http://localhost:4173.

**On your phone (same Wi-Fi):** open **http://192.168.12.124:4173** while that command is running.
- If Windows asks whether to allow Node.js, allow it on private networks.
- Use `serve` rather than `python -m http.server`. Python's server can't send video in pieces (byte-range requests), and iPhones won't play video without that.
- Double-clicking `index.html` also works on desktop, but the saved contact won't include the photo (the browser blocks reading local files from `file://`).

## Verification (builder)
The checks ran in headless Chrome against `http://192.168.12.124:4173/`, at 390 px phone width (3× pixel density, touch) and at 1440 px desktop. Screenshots and a sample contact file are in `Unit01_verification/`.

| Check | Result |
|---|---|
| Hero plays muted, inline and looping; poster paints first | Pass. Plays at 1080×1080 and runs past the loop point cleanly. |
| Flip by tap and by keyboard; video pauses while flipped | Pass |
| QR opens and closes (tap, Enter, Esc), with focus handled | Pass |
| QR decodes to the page URL with a real reader (zxing-cpp) | Pass. `http://192.168.12.124:4173/` from the phone, desktop and tile screenshots, and from the phone screenshot shrunk to ¼. |
| Share | Pass. Hands the URL to the share sheet; without one, it copies the link and says so. |
| Save | Pass. Downloads `Nate Ivy.vcf`. A vCard parser (vobject) reads: N Nathan / Ivy, FN Nathan Ivy, NICKNAME Nate, ORG NextSketch, TITLE Lead Product Architect & CEO, a Website URL, a LinkedIn URL, a 480×480 JPEG photo, and EMAIL (work) nate@nextsketch.com. No phone or address. Lines use CRLF and are folded at 75 bytes. |
| Only website and LinkedIn; no empty or dead buttons | Pass |
| Outside network requests | **0.** All 10 requests go to the page's own server; the only other resource is an inline `data:` image. |
| Page weight, first visit with no cache | **0.92 MB transferred** (about 1.0 MB uncompressed). Reduced motion: 0.24 MB, because the video never downloads. |
| Console errors or warnings | None |
| Reduced motion | Pass. Poster only, no entrance or flip animation. |

## Differences from the brief and reference (for Nate's review)
1. **Hero clip is a web copy, not the master file.** The master is 3.5 MB, more than the whole 3 MB page budget (D4). The copy is the same footage scaled to 1080² at high quality; it scores 0.995 SSIM against the master, which means visually the same. Of the master's 121 frames, the last one repeats the one before it, so the copy keeps 120 frames. Without that repeat, the loop runs straight through without a stall. The master in `assets/` is untouched.
2. **The editable block lives at the top of `index.html`**, not in a separate config file. Link previews (iMessage, LinkedIn, Slack) only read static `<title>`/`<meta>` tags, so keeping those tags and the config in one block keeps everything in one place.
3. **Saved contact name:** the contact is saved as Nathan Ivy (first name Nathan, last name Ivy) with nickname Nate, per D10. The card itself shows "Nate Ivy".
4. **No address in the saved contact.** Nate's answer to gap 9. The reference saved one.
5. **Quick-action row left out**: nothing qualifies under D11. It comes back automatically for P2.
6. **Footer:** the cream logo plus "© 2026 Next Sketch LLC", from the nextsketch.com footer. It replaces Josh's personal line.
7. **Back of the flip (D7):** dark logo, then "From idea to production.", then "You’re not hiring a vendor. You’re gaining a product partner." Both lines are word for word from the nextsketch.com hero.
8. **Company is spelled "NextSketch"** everywhere except the legal footer line, to match the logo and site copy.
9. **The reference's on-screen labels are kept word for word**, with one change: its failure message pointed people to call and email buttons that don't exist here. It now reads "Could not download the contact card."
10. **QR code** is generated in the page instead of fetched from `api.qrserver.com` (D4). It's dark on a cream tile with a 4-module quiet zone, which scanners need. It encodes the page's own URL without any `#…` part.
11. **Small reliability and accessibility additions that don't change the look:**
    - The "Tap" hint is a real button, so the flip works from the keyboard.
    - The QR panel is a proper dialog: Esc closes it and focus returns to the QR button.
    - The video pauses while the card is flipped.
    - The front face is hidden at the edge-on point of the flip, because some Safari versions let video show through the back face.
    - The Share and QR buttons switch to dark-on-cream when the card is flipped.
    - The iPhone Low Power Mode play button is hidden; the poster simply stays put.
12. **No link-preview image (`og:image`).** It needs an absolute URL, which only exists after deploy. Add it at the deploy step.
13. **Badges changed by Nate after the build (replaces D8 wording):** "Product Development" and "AI Integrations" (were "AI-First Product Development" and "AI Workflow Integration"). They now fit on one row.
14. **Email added by Nate after the build (changes D11):** `nate@nextsketch.com` is in the saved contact, labelled as a work email. It isn't shown on the card.

## Open for Nate
- **G2: test Save on your iPhone.** The download is verified in Chrome. iOS should show its contact sheet or a download prompt, and then "Create New Contact". If it doesn't, the fallback is a static `.vcf` file in the folder.
- **Share on the phone preview** uses the copy fallback, because the share sheet needs HTTPS. The real share sheet gets tested at G3.
- **`.claude/`** in the build folder was created by the Claude Code session, not the site. `.vercelignore` keeps it out of a Vercel deploy. Leave it out on any other host too.
- **Once cards are printed with the Vercel URL, never rename or delete that Vercel project** (sprint risk table).

## Dev-only tooling (not shipped; lives in the session scratchpad)
- ffmpeg (via `imageio-ffmpeg`) for the clip.
- Pillow for the contact photo.
- puppeteer-core with installed Chrome for icons, screenshots and checks.
- zxing-cpp for QR decoding.
- vobject for parsing the contact file.
- `serve` for the local server.
- Fonts from `@fontsource-variable`; QR library from `qrcode-generator` (npm).

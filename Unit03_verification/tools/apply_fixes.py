"""Unit 03 mechanical fixes to index.html. Every replacement is exact and must match exactly once.
usage: python -I apply_fixes.py <in.html> <out.html>
"""
import sys

raw = open(sys.argv[1], encoding="utf8", newline="").read()
CRLF = "\r\n" in raw          # the working tree is CRLF (git stores LF); keep whatever it is
src = raw.replace("\r\n", "\n")
n_applied = 0


def rep(old, new, count=1):
    global src, n_applied
    found = src.count(old)
    assert found == count, f"expected {count} match(es), found {found}:\n{old[:200]}"
    src = src.replace(old, new)
    n_applied += 1


# ---------------------------------------------------------------- 1. the token block, moved to the top of the styles
OLD_FONTFACE = """<style>
  @font-face {
    font-family: "Inter";
    src: url("fonts/inter.woff2") format("woff2");
    font-weight: 100 900; font-style: normal; font-display: swap;
  }
  @font-face {
    font-family: "Playfair Display";
    src: url("fonts/playfair-display.woff2") format("woff2");
    font-weight: 400 900; font-style: normal; font-display: swap;
  }
  @font-face {
    font-family: "JetBrains Mono";
    src: url("fonts/jetbrains-mono.woff2") format("woff2");
    font-weight: 100 800; font-style: normal; font-display: swap;
  }

  :root {
    color-scheme: dark;
    /* Fin's dark set (zen-linen-fin.css, .dark). These are the card's only colours. */
    --sidebar: #101010;            /* fin's darkest step: the page behind the card */
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
    --ring: #D1CFC0;
    --brand: #F26A4B;              /* coral: the one accent */

    /* Fin's radius scale: every step derives from one token (app/globals.css). */
    --radius: 0.5rem;
    --radius-md: calc(var(--radius) * 0.8);
    --radius-lg: var(--radius);
    --radius-xl: calc(var(--radius) * 1.4);

    /* Fin's soft shadow scale. Near-invisible in dark on purpose: the border separates. */
    --shadow-xs: 0 1px 4px 1px rgb(0 0 0 / 0.04);
    --shadow-lg: 0 8px 30px 5px rgb(0 0 0 / 0.06);
    --shadow-xl: 0 14px 44px 7px rgb(0 0 0 / 0.07);

    --sans: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    --serif: "Playfair Display", Georgia, "Times New Roman", serif;
    --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;

    --ease: cubic-bezier(.22, 1, .36, 1);  /* the flip (Unit 01 timing) */
    --fast: 150ms;                         /* every state change: fin §8, under 200ms */
  }
"""
NEW_TOKENS = """<style>
  /* ==================================================================
     THE CARD'S TOKENS: the one place a value is written (Unit 03 standard).
     Every colour, radius, shadow, font, type size and motion time the card
     uses is declared here, once, under fin's name where fin has one.
     Rules below read var() only. The two exceptions, each commented where
     it is used: black transparencies for an overlay or a shadow, and the
     keywords transparent / currentColor (no colour of their own).
     ================================================================== */
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

  @font-face {
    font-family: "Inter";
    src: url("fonts/inter.woff2") format("woff2");
    font-weight: 100 900; font-style: normal; font-display: swap;
  }
  @font-face {
    font-family: "Playfair Display";
    src: url("fonts/playfair-display.woff2") format("woff2");
    font-weight: 400 900; font-style: normal; font-display: swap;
  }
  @font-face {
    font-family: "JetBrains Mono";
    src: url("fonts/jetbrains-mono.woff2") format("woff2");
    font-weight: 100 800; font-style: normal; font-display: swap;
  }
"""
rep(OLD_FONTFACE, NEW_TOKENS)

# ---------------------------------------------------------------- 2. base
rep("    font-family: var(--sans);\n", "    font-family: var(--font-sans);\n")
rep("  .reveal { animation: rise .6s cubic-bezier(.2, .7, .2, 1) backwards; }",
    "  .reveal { animation: rise var(--duration-entrance) var(--ease-entrance) backwards; }")

# ---------------------------------------------------------------- 3. interaction base + the button recipe (.btn base, four variants)
rep("""  /* ---------- interaction: fin's INTERACTIVE base, on every control ---------- */
  .icon-btn, .flip-hint, .save, .link, .quick a, .qr-close {
    cursor: pointer; outline: none; touch-action: manipulation;
    transition: color var(--fast), background-color var(--fast), border-color var(--fast), opacity var(--fast);
  }

  /* ---------- icon buttons: button.tsx outline variant, icon size ---------- */
  .icon-btn {
    width: 36px; height: 36px; padding: 0; display: grid; place-items: center;
    border-radius: var(--radius-md); border: 1px solid var(--border);
    background: rgb(44 44 44 / 0.3);   /* dark:bg-input/30 */
    color: var(--foreground); box-shadow: var(--shadow-xs);
  }
  .icon-btn svg { width: 16px; height: 16px; }
  .icon-btn:active { background: var(--muted); }
  .icon-btn:disabled { pointer-events: none; opacity: .5; }
""", """  /* ---------- interaction: fin's INTERACTIVE base, on every control ---------- */
  .btn, .link, .quick a {
    cursor: pointer; outline: none; touch-action: manipulation;
    transition: color var(--duration-fast), background-color var(--duration-fast), border-color var(--duration-fast), opacity var(--duration-fast);
  }

  /* ---------- Button: button.tsx. Every button carries .btn plus one variant class:
       .save = default (primary) · .icon-btn = outline, icon size · .flip-hint = ghost
       · .qr-close = dialog.tsx close. States live in the state blocks further down. ---------- */
  .btn { border-radius: var(--radius-md); }
  .btn svg { width: 16px; height: 16px; }
  .btn:disabled { pointer-events: none; opacity: .5; }

  /* Outline variant, icon size (Share, QR). */
  .icon-btn {
    width: 36px; height: 36px; padding: 0; display: grid; place-items: center;
    border: 1px solid var(--input); background: var(--input-30);
    color: var(--foreground); box-shadow: var(--shadow-xs);
  }

  /* ---------- Label: fin's eyebrow step. The one recipe for every mono label. ---------- */
  .eyebrow, .flip-hint, .badge, .divider, .qr-heading {
    font-family: var(--font-mono); font-size: var(--text-eyebrow); font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
  }
""")

# ---------------------------------------------------------------- 4. hero + flip
rep("    transform-style: preserve-3d; transition: transform .7s var(--ease);",
    "    transform-style: preserve-3d; transition: transform var(--duration-flip) var(--ease-flip);")
rep("    transition: visibility 0s linear .09s;", "    transition: visibility 0s linear var(--delay-face-swap);")
rep("  .portrait-video { opacity: 0; transition: opacity .4s ease; }",
    "  .portrait-video { opacity: 0; transition: opacity var(--duration-fade) ease; }")
rep("""    background: linear-gradient(180deg, rgb(20 20 20 / 0) 34%, rgb(20 20 20 / 0.6) 60%, rgb(20 20 20 / 0.9) 76%, var(--background) 100%);""",
    """    background: linear-gradient(180deg, var(--background-0) 34%, var(--background-60) 60%, var(--background-90) 76%, var(--background) 100%);""")
rep("""  .eyebrow {
    margin: 0 0 10px; font-family: var(--mono); font-size: 11px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--brand);
  }
  .name {
    margin: 0; font-family: var(--serif); font-weight: 700; font-size: 38px; line-height: 1.08; letter-spacing: -0.025em;
    color: var(--foreground); text-shadow: 0 2px 18px rgb(0 0 0 / 0.5);
  }

  /* "Tap" hint: button.tsx ghost variant, on fin's 11px label step. */
  .flip-hint {
    position: absolute; bottom: 14px; right: 14px; z-index: 2;
    display: inline-flex; align-items: center; gap: 6px; height: 32px; padding: 0 10px;
    border: 1px solid transparent; border-radius: var(--radius-md); background: none;
    font-family: var(--mono); font-size: 11px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted-foreground);
  }
  .flip-hint svg { width: 14px; height: 14px; }
  .flip-hint:active { background: var(--accent); color: var(--foreground); }
""", """  .eyebrow { margin: 0 0 10px; color: var(--brand); }
  .name {
    margin: 0; font-family: var(--font-serif); font-weight: 700; font-size: var(--text-display); line-height: 1.08; letter-spacing: -0.025em;
    color: var(--foreground);
    text-shadow: 0 2px 18px rgb(0 0 0 / 0.5);   /* black transparency: legibility over the clip (Unit 01), not elevation */
  }

  /* "Tap" hint: button.tsx ghost variant, on the label recipe. */
  .flip-hint {
    position: absolute; bottom: 14px; right: 14px; z-index: 2;
    display: inline-flex; align-items: center; gap: 6px; height: 32px; padding: 0 10px;
    border: 1px solid transparent; background: none;
    color: var(--muted-foreground);
  }
  .flip-hint svg { width: 14px; height: 14px; }
""")
rep("""    margin: 0 0 14px; font-family: var(--serif); font-weight: 700; font-size: 27px;""",
    """    margin: 0 0 14px; font-family: var(--font-serif); font-weight: 700; font-size: var(--text-display-sm);""")
rep("  .back-body { font-size: 14px; line-height: 1.55; color: var(--muted-foreground); }",
    "  .back-body { font-size: var(--text-sm); line-height: 1.55; color: var(--muted-foreground); }")

# ---------------------------------------------------------------- 5. content
rep("  .role { margin: 0 0 16px; font-size: 14px; line-height: 1.5; color: var(--muted-foreground); }",
    "  .role { margin: 0 0 16px; font-size: var(--text-sm); line-height: 1.5; color: var(--muted-foreground); }")
rep("""  /* Badges: no fin equivalent. Fin's pill shape on its secondary surface, its 11px
     label step, and the site's coral diamond as the marker. */
  .badges { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 22px; }
  .badge {
    display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px;
    font-family: var(--mono); font-size: 11px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--foreground); border: 1px solid var(--border); border-radius: 999px; background: var(--secondary);
  }""", """  /* Badges: no fin equivalent. Fin's pill shape on its secondary surface, the label
     recipe, and the site's coral diamond as the marker. */
  .badges { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 22px; }
  .badge {
    display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px;
    color: var(--foreground); border: 1px solid var(--border); border-radius: var(--radius-full); background: var(--secondary);
  }""")
rep("""  /* Save: button.tsx default (primary) variant. */
  .save {
    width: 100%; height: 48px; display: flex; align-items: center; justify-content: center; gap: 8px;
    padding: 0 24px; border: 0; border-radius: var(--radius-md); text-decoration: none;
    font-size: 16px; font-weight: 500; color: var(--primary-foreground); background: var(--primary);
  }
  .save svg { width: 16px; height: 16px; flex: none; }
  .save:active { background: rgb(209 207 192 / 0.8); }
  .save:not([href]) { opacity: .5; cursor: default; }

  /* Quick-action tiles (off until P2): fin's card surface, same states as the link rows. */
  .quick { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 8px; }
  .quick[hidden] { display: none; }
  .quick a {
    display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px 6px;
    border-radius: var(--radius-lg); border: 1px solid var(--border); background: var(--card);
    color: var(--foreground); text-decoration: none; font-size: 12px; font-weight: 500;
  }
  .quick a svg { width: 18px; height: 18px; color: var(--brand); }
  .quick a:active { background: var(--muted); }

  .divider {
    display: flex; align-items: center; gap: 12px; margin: 24px 2px 14px;
    font-family: var(--mono); font-size: 11px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted-foreground);
  }
  .divider::before, .divider::after { content: ""; height: 1px; flex: 1; background: var(--border); }

  /* Link rows: fin's card surface (card fill, border hairline, radius-lg). */
  .links { display: flex; flex-direction: column; gap: 8px; }
  .link {
    display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: var(--radius-lg);
    border: 1px solid var(--border); background: var(--card);
    color: var(--foreground); text-decoration: none;
  }
  .link-icon""", """  /* Save: button.tsx default (primary) variant. Its disabled state is :not([href]): it stays
     clickable so the failure toast can still show (Unit 02, difference 5). */
  .save {
    width: 100%; height: 48px; display: flex; align-items: center; justify-content: center; gap: 8px;
    padding: 0 24px; border: 0; text-decoration: none;
    font-size: var(--text-base); font-weight: 500; color: var(--primary-foreground); background: var(--primary);
  }
  .save svg { flex: none; }
  .save:not([href]) { opacity: .5; cursor: default; }

  /* ---------- Card surface: fin's card (--card fill, --border hairline, radius-lg).
       The one recipe for link rows and quick-action tiles; their states are shared too. ---------- */
  .link, .quick a {
    border-radius: var(--radius-lg); border: 1px solid var(--border); background: var(--card);
    color: var(--foreground); text-decoration: none;
  }

  /* Quick-action tiles (off until P2). */
  .quick { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 8px; }
  .quick[hidden] { display: none; }
  .quick a {
    display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px 6px;
    font-size: var(--text-xs); font-weight: 500;
  }
  .quick a svg { width: 18px; height: 18px; color: var(--brand); }

  .divider {
    display: flex; align-items: center; gap: 12px; margin: 24px 2px 14px;
    color: var(--muted-foreground);
  }
  .divider::before, .divider::after { content: ""; height: 1px; flex: 1; background: var(--border); }

  /* Link rows. */
  .links { display: flex; flex-direction: column; gap: 8px; }
  .link { display: flex; align-items: center; gap: 12px; padding: 12px 16px; }
  .link-icon""")
rep("""  .link-name { font-size: 14px; font-weight: 500; }
  .link-sub { font-size: 12px; color: var(--muted-foreground); }
  .link-arrow { margin-left: auto; color: var(--muted-foreground); display: grid; transition: color var(--fast); }
  .link-arrow svg { width: 16px; height: 16px; }
  /* Pressed: muted text would be 4.2:1 on --muted, so it lifts to linen. */
  .link:active { background: var(--muted); border-color: var(--accent); }
  .link:active .link-sub, .link:active .link-arrow { color: var(--foreground); }
""", """  .link-name { font-size: var(--text-sm); font-weight: 500; }
  .link-sub { font-size: var(--text-xs); color: var(--muted-foreground); }
  .link-arrow { margin-left: auto; color: var(--muted-foreground); display: grid; transition: color var(--duration-fast); }
  .link-arrow svg { width: 16px; height: 16px; }
""")
rep("  .foot p { font-size: 11px; letter-spacing: 0.04em; color: var(--muted-foreground); }",
    "  .foot p { font-size: var(--text-eyebrow); letter-spacing: 0.04em; color: var(--muted-foreground); }")

# ---------------------------------------------------------------- 6. states: hover, then one active block, then focus
rep("""  /* ---------- hover: only where there is a pointer that hovers, so it never sticks after a tap ---------- */
  @media (hover: hover) {
    .icon-btn:hover { background: rgb(44 44 44 / 0.5); }   /* dark:hover:bg-input/50 */
    .icon-btn:active { background: var(--muted); }
    .flip-hint:hover { background: rgb(54 54 54 / 0.5); color: var(--foreground); }   /* dark:hover:bg-accent/50 */
    .flip-hint:active { background: var(--accent); }
    .save:hover { background: rgb(209 207 192 / 0.9); }   /* hover:bg-primary/90 */
    .save:active { background: rgb(209 207 192 / 0.8); }
    .link:hover, .quick a:hover { background: var(--secondary); border-color: var(--accent); }
    .link:hover .link-arrow { color: var(--foreground); }
    .link:active, .quick a:active { background: var(--muted); }
    .qr-close:hover { opacity: 1; }
  }
""", """  /* ---------- states, in this order: hover → active → focus-visible → touch floor ---------- */

  /* hover: only where there is a pointer that hovers, so it never sticks after a tap */
  @media (hover: hover) {
    .icon-btn:hover { background: var(--input-50); }
    .flip-hint:hover { background: var(--accent-50); color: var(--foreground); }
    .save:hover { background: var(--primary-90); }
    .link:hover, .quick a:hover { background: var(--secondary); border-color: var(--accent); }
    .link:hover .link-arrow { color: var(--foreground); }
    .qr-close:hover { opacity: 1; }
  }

  /* active (pressed): everywhere, touch included. After hover, so a pressed control shows pressed. */
  .icon-btn:active { background: var(--muted); }
  .flip-hint:active { background: var(--accent); color: var(--foreground); }
  .save:active { background: var(--primary-80); }
  .link:active, .quick a:active { background: var(--muted); }
  .link:active { border-color: var(--accent); }
  /* Pressed: muted text would be 4.2:1 on --muted, so it lifts to linen. */
  .link:active .link-sub, .link:active .link-arrow { color: var(--foreground); }
  .qr-close:active { opacity: 1; background: var(--muted); }
""")

# ---------------------------------------------------------------- 7. QR sheet + toast
rep("""    opacity: 0; visibility: hidden; transition: opacity var(--fast), visibility 0s linear var(--fast);
  }
  .qr.is-open { opacity: 1; visibility: visible; transition: opacity var(--fast); }
  .qr-overlay { position: absolute; inset: 0; background: rgb(0 0 0 / 0.5); }""",
    """    opacity: 0; visibility: hidden; transition: opacity var(--duration-fast), visibility 0s linear var(--duration-fast);
  }
  .qr.is-open { opacity: 1; visibility: visible; transition: opacity var(--duration-fast); }
  .qr-overlay { position: absolute; inset: 0; background: rgb(0 0 0 / 0.5); }   /* black/50: fin's dialog overlay */""")
rep("    transform: scale(.95); transition: transform var(--fast);",
    "    transform: scale(.95); transition: transform var(--duration-fast);")
rep("""  .qr-close {
    position: absolute; top: 16px; right: 16px; width: 28px; height: 28px; padding: 0;
    display: grid; place-items: center; border: 1px solid transparent; border-radius: var(--radius-md);
    background: none; color: var(--foreground); opacity: .7;
  }
  .qr-close svg { width: 16px; height: 16px; }
  .qr-close:active { opacity: 1; background: var(--muted); }
  .qr-heading {
    margin: 4px 0 20px; font-family: var(--mono); font-size: 11px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted-foreground);
  }""", """  /* Close: dialog.tsx. Known defect (Unit 03, finding F1): this rule sits after the touch
     floor, so on touch it wins and Close stays 28px instead of 44px. Left as built pending Nate. */
  .qr-close {
    position: absolute; top: 16px; right: 16px; width: 28px; height: 28px; padding: 0;
    display: grid; place-items: center; border: 1px solid transparent;
    background: none; color: var(--foreground); opacity: .7;
  }
  .qr-heading { margin: 4px 0 20px; color: var(--muted-foreground); }""")
rep("""  .qr-name { margin: 20px 0 0; font-family: var(--serif); font-size: 24px; font-weight: 700; letter-spacing: -0.02em; color: var(--foreground); }
  .qr-caption { margin: 6px 0 0; font-size: 14px; color: var(--muted-foreground); text-align: center; }""",
    """  .qr-name { margin: 20px 0 0; font-family: var(--font-serif); font-size: var(--text-2xl); font-weight: 700; letter-spacing: -0.02em; color: var(--foreground); }
  .qr-caption { margin: 6px 0 0; font-size: var(--text-sm); color: var(--muted-foreground); text-align: center; }""")
rep("""    max-width: 88vw; padding: 12px 16px; border-radius: var(--radius-lg); font-size: 14px; overflow-wrap: anywhere;""",
    """    max-width: 88vw; padding: 12px 16px; border-radius: var(--radius-lg); font-size: var(--text-sm); overflow-wrap: anywhere;""")
rep("    opacity: 0; pointer-events: none; transition: opacity var(--fast), transform var(--fast);",
    "    opacity: 0; pointer-events: none; transition: opacity var(--duration-fast), transform var(--duration-fast);")

# ---------------------------------------------------------------- 8. markup: every button carries .btn
rep('<button class="icon-btn" id="share-btn"', '<button class="btn icon-btn" id="share-btn"')
rep('<button class="icon-btn" id="qr-btn"', '<button class="btn icon-btn" id="qr-btn"')
rep('<button class="flip-hint" id="flip-to-back"', '<button class="btn flip-hint" id="flip-to-back"')
rep('<button class="flip-hint" id="flip-to-front"', '<button class="btn flip-hint" id="flip-to-front"')
rep('<a class="save reveal" id="save"', '<a class="btn save reveal" id="save"')
rep('<button class="qr-close" id="qr-close"', '<button class="btn qr-close" id="qr-close"')

open(sys.argv[2], "w", encoding="utf8", newline="").write(src.replace("\n", "\r\n") if CRLF else src)
print(f"applied {n_applied} replacements")

"""Build the committed evidence from a capture run: JPEG page states + one states sheet per width.
usage: python -I evidence.py <captureDir> <outDir> <label>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

cap, out, label = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
CONTROLS = ["share-btn", "qr-btn", "flip-to-back", "flip-to-front", "save", "link-1", "link-2", "qr-close"]
PAGES = ["front", "flipped", "qr-viewport", "toast-share", "toast-save", "reduced"]
try:
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
except OSError:
    font = ImageFont.load_default()

for vp in ("phone", "desktop"):
    d = cap / vp
    for p in PAGES:
        im = Image.open(d / f"{p}.png").convert("RGB")
        if vp == "phone":  # 3x captures: halve for the record, the pixel proof is in the compare report
            im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
        im.save(out / f"{label}-{vp}-{p}.jpg", quality=82, optimize=True)

    # states sheet: one row per control, columns = focus (real Tab), hover, active, disabled
    cols = ["focus", "hover", "active", "disabled"]
    cells = {}
    for c in CONTROLS:
        for s in cols:
            f = d / f"{s}-{c}.png"
            if f.exists():
                im = Image.open(f).convert("RGB")
                if vp == "phone":
                    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
                cells[(c, s)] = im
    colw = {s: max([cells[(c, s)].width for c in CONTROLS if (c, s) in cells] or [60]) for s in cols}
    rowh = {c: max([cells[(c, s)].height for s in cols if (c, s) in cells] or [20]) for c in CONTROLS}
    lw, gap, head = 130, 10, 30
    W = lw + sum(colw.values()) + gap * (len(cols) + 1)
    H = head + sum(rowh.values()) + gap * (len(CONTROLS) + 1)
    sheet = Image.new("RGB", (W, H), (245, 245, 245))
    dr = ImageDraw.Draw(sheet)
    x = lw + gap
    for s in cols:
        dr.text((x, 8), s + (" (Tab)" if s == "focus" else " (n/a touch)" if s == "hover" and vp == "phone" else ""), fill=(20, 20, 20), font=font)
        x += colw[s] + gap
    y = head + gap
    for c in CONTROLS:
        dr.text((8, y + 4), c, fill=(20, 20, 20), font=font)
        x = lw + gap
        for s in cols:
            if (c, s) in cells:
                sheet.paste(cells[(c, s)], (x, y))
            x += colw[s] + gap
        y += rowh[c] + gap
    sheet.save(out / f"{label}-{vp}-states-sheet.jpg", quality=88, optimize=True)
print("ok", sorted(p.name for p in out.glob(f"{label}-*")))

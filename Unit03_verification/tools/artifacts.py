"""QR decode (zxing-cpp) and vCard parse (vobject) for one capture + behaviour run.
usage: python -I artifacts.py <captureDir> <behaviourDir> <projectDir> <expectedUrl>
"""
import base64
import hashlib
import json
import sys
from pathlib import Path

import vobject
import zxingcpp
from PIL import Image

cap, beh, proj, url = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
out = {"qr": [], "vcard": []}

for vp in ("phone", "desktop"):
    for name in ("qr-tile.png", "qr-viewport.png", "qr.png"):
        im = Image.open(cap / vp / name).convert("RGB")
        for scale in (1, 4):
            s = im if scale == 1 else im.resize((max(1, im.width // 4), max(1, im.height // 4)), Image.LANCZOS)
            res = zxingcpp.read_barcodes(s)
            texts = [r.text for r in res if r.format == zxingcpp.BarcodeFormat.QRCode]
            out["qr"].append({"vp": vp, "file": name, "scale": f"1/{scale}", "decoded": texts, "pass": texts == [url]})

photo_ref = (proj / "media" / "contact.jpg").read_bytes()
for vp in ("phone", "desktop"):
    files = sorted((beh / f"{vp}-download").glob("*.vcf"))
    if not files:
        out["vcard"].append({"vp": vp, "pass": False, "error": "no download"})
        continue
    raw = files[0].read_bytes()
    text = raw.decode("utf-8")
    lines = raw.split(b"\r\n")
    card = vobject.readOne(text)
    photo = card.photo.value if hasattr(card, "photo") else b""
    if isinstance(photo, str):
        photo = base64.b64decode(photo)
    w = h = None
    if photo:
        import io
        w, h = Image.open(io.BytesIO(photo)).size
    entry = {
        "vp": vp, "file": files[0].name, "bytes": len(raw),
        "crlfOnly": b"\n" not in raw.replace(b"\r\n", b""),
        "maxLineBytes": max(len(l) for l in lines),
        "N": str(card.n.value), "FN": card.fn.value,
        "NICKNAME": getattr(card, "nickname").value if hasattr(card, "nickname") else None,
        "ORG": card.org.value if hasattr(card, "org") else None,
        "TITLE": card.title.value if hasattr(card, "title") else None,
        "EMAIL": card.email.value if hasattr(card, "email") else None,
        "TEL": card.tel.value if hasattr(card, "tel") else None,
        "ADR": card.adr.value if hasattr(card, "adr") else None,
        "URLs": [c.value for c in card.getChildren() if c.name == "URL"],
        "photo": {"bytes": len(photo), "size": f"{w}x{h}", "sha256": hashlib.sha256(photo).hexdigest()[:16],
                  "identicalToContactJpg": photo == photo_ref},
    }
    entry["pass"] = entry["crlfOnly"] and entry["maxLineBytes"] <= 75 and entry["photo"]["identicalToContactJpg"] and entry["TEL"] is None and entry["ADR"] is None
    out["vcard"].append(entry)

(beh / "artifacts.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf8")
print(json.dumps(out, indent=1, default=str))

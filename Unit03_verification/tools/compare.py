"""Compare two capture runs: every PNG pixel-for-pixel, every computed-style dump property-for-property.
usage: python -I compare.py <dirA> <dirB> [report.json]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

a_root, b_root = Path(sys.argv[1]), Path(sys.argv[2])
report = {"images": [], "styles": [], "summary": {}}
img_total = img_same = sty_total = sty_same = 0

for vp in ("phone", "desktop"):
    a, b = a_root / vp, b_root / vp
    for pa in sorted(a.glob("*.png")):
        pb = b / pa.name
        img_total += 1
        if not pb.exists():
            report["images"].append({"vp": vp, "file": pa.name, "result": "missing in B"})
            continue
        ia = np.asarray(Image.open(pa).convert("RGBA"), dtype=np.int16)
        ib = np.asarray(Image.open(pb).convert("RGBA"), dtype=np.int16)
        if ia.shape != ib.shape:
            report["images"].append({"vp": vp, "file": pa.name, "result": f"size {ia.shape} vs {ib.shape}"})
            continue
        d = np.abs(ia - ib)
        n = int((d.max(axis=2) > 0).sum())
        entry = {"vp": vp, "file": pa.name, "size": f"{ia.shape[1]}x{ia.shape[0]}", "pixelsDiffering": n, "maxChannelDelta": int(d.max())}
        report["images"].append(entry)
        img_same += n == 0
    for ja in sorted(a.glob("styles-*.json")):
        jb = b / ja.name
        sty_total += 1
        A = json.loads(ja.read_text(encoding="utf8"))
        B = json.loads(jb.read_text(encoding="utf8")) if jb.exists() else {}
        diffs = []
        for k in sorted(set(A) | set(B)):
            if k not in A or k not in B:
                diffs.append({"el": k, "only": "A" if k in A else "B"})
                continue
            for p in sorted(set(A[k]) | set(B[k])):
                if A[k].get(p) != B[k].get(p):
                    diffs.append({"el": k, "prop": p, "A": A[k].get(p), "B": B[k].get(p)})
        props = sum(len(v) for v in A.values())
        report["styles"].append({"vp": vp, "file": ja.name, "elements": len(A), "properties": props, "diffs": diffs[:50], "diffCount": len(diffs)})
        sty_same += not diffs

report["summary"] = {
    "images": f"{img_same}/{img_total} pixel-identical",
    "styleDumps": f"{sty_same}/{sty_total} identical (custom properties excluded)",
    "propertiesCompared": sum(s["properties"] for s in report["styles"]),
}
out = Path(sys.argv[3]) if len(sys.argv) > 3 else None
if out:
    out.write_text(json.dumps(report, indent=1), encoding="utf8")
print(json.dumps(report["summary"]))
for e in report["images"]:
    if e.get("pixelsDiffering", 1):
        print("IMG DIFF", e)
for s in report["styles"]:
    if s["diffCount"]:
        print("STYLE DIFF", s["vp"], s["file"], s["diffCount"], s["diffs"][:5])

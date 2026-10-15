"""Dead-code sweep for index.html: CSS classes, ids, custom properties, keyframes, script functions.
usage: python -I dead.py index.html
"""
import re
import sys

src = open(sys.argv[1], encoding="utf8").read()
style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
style_nc = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
body = src[src.index("</style>"):]
head_scripts = "".join(re.findall(r"<script>(.*?)</script>", src[: src.index("<style>")], re.S))
markup_and_js = body + head_scripts

# --- classes: defined in CSS vs used in class="" or in script strings
css_classes = set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"url\([^)]*\)|\d+\.\d+|\.\d+", "", style_nc)))
used = set()
for m in re.findall(r'class="([^"]+)"', markup_and_js):
    used.update(m.split())
for m in re.findall(r"""["']([a-z][\w-]*(?: [a-z][\w-]*)*)["']""", markup_and_js):
    used.update(m.split())
dead_classes = sorted(c for c in css_classes if c not in used)
print("CSS classes:", len(css_classes), "| unused:", dead_classes or "none")

# --- custom properties: declared vs read with var()
declared = re.findall(r"(--[\w-]+)\s*:", style_nc)
read = set(re.findall(r"var\((--[\w-]+)", style_nc))
dupes = sorted({d for d in declared if declared.count(d) > 1})
print("custom properties declared:", len(declared), "| declared twice:", dupes or "none",
      "| never read:", sorted(set(declared) - read) or "none", "| read but never declared:", sorted(read - set(declared)) or "none")

# --- ids referenced by script must exist, ids in markup should be referenced
ids = set(re.findall(r'id="([^"]+)"', body))
script = "".join(re.findall(r"<script>(.*?)</script>", body, re.S))
ref = set(re.findall(r'\$\("([^"]+)"\)', script)) | set(re.findall(r'(?:aria-labelledby|aria-describedby|aria-controls|for)="([^"]+)"', body))
print("ids:", len(ids), "| referenced by script/ARIA but missing:", sorted(ref - ids) or "none",
      "| never referenced (styled by id or anchors only):", sorted(ids - ref) or "none")

# --- keyframes
kf = re.findall(r"@keyframes\s+([\w-]+)", style_nc)
print("keyframes:", kf, "| unused:", [k for k in kf if not re.search(r"animation[^;]*\b" + k + r"\b", style_nc)] or "none")

# --- script: functions and vars declared but never used again
decl = re.findall(r"function\s+(\w+)\s*\(", script) + re.findall(r"var\s+(\w+)\s*=", script) + re.findall(r",\s*(\w+)\s*=\s*(?!=)", script)
unused = sorted({d for d in decl if len(re.findall(r"\b" + re.escape(d) + r"\b", script)) < 2})
print("script names declared:", len(set(decl)), "| used only once (declared, never read):", unused or "none")

# --- icon keys offered vs reachable from the edit block
icons = re.findall(r"^\s{4}(\w+): '<svg", script, re.M)
print("ICONS keys:", icons, "(website/linkedin/instagram/x/youtube/tiktok are the edit block's documented options; phone/mail serve quickActions)")

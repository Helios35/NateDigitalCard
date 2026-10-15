"""Find CSS named colours used as values in index.html outside the token block.
usage: python -I named_colours.py index.html <tokenStart> <tokenEnd>
Comments are stripped first, so "linen" in a comment is not a hit; a value like `color: tan` is.
"""
import re
import sys

NAMED = """aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond blue blueviolet brown
burlywood cadetblue chartreuse chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan darkgoldenrod
darkgray darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid darkred darksalmon darkseagreen
darkslateblue darkslategray darkslategrey darkturquoise darkviolet deeppink deepskyblue dimgray dimgrey dodgerblue
firebrick floralwhite forestgreen fuchsia gainsboro ghostwhite gold goldenrod gray green greenyellow grey honeydew
hotpink indianred indigo ivory khaki lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan
lightgoldenrodyellow lightgray lightgreen lightgrey lightpink lightsalmon lightseagreen lightskyblue lightslategray
lightslategrey lightsteelblue lightyellow lime limegreen linen magenta maroon mediumaquamarine mediumblue mediumorchid
mediumpurple mediumseagreen mediumslateblue mediumspringgreen mediumturquoise mediumvioletred midnightblue mintcream
mistyrose moccasin navajowhite navy oldlace olive olivedrab orange orangered orchid palegoldenrod palegreen
paleturquoise palevioletred papayawhip peru pink plum powderblue purple rebeccapurple red rosybrown royalblue
saddlebrown salmon sandybrown seagreen seashell sienna silver skyblue slateblue slategray slategrey snow springgreen
steelblue tan teal thistle tomato turquoise violet wheat white whitesmoke yellow yellowgreen""".split()
KEYWORDS = ["transparent", "currentColor", "currentcolor"]

path, t0, t1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
lines = open(path, encoding="utf8").read().split("\n")
src = "\n".join("" if t0 <= i + 1 <= t1 else l for i, l in enumerate(lines))
# strip CSS/JS block comments and HTML comments, keep line numbers
strip = lambda m: re.sub(r"[^\n]", " ", m.group(0))
src = re.sub(r"/\*.*?\*/", strip, src, flags=re.S)
src = re.sub(r"<!--.*?-->", strip, src, flags=re.S)
src = re.sub(r"(?m)^\s*//.*$", strip, src)
# colour-bearing contexts: CSS declarations, SVG paint attributes, theme-color
ctx = re.compile(r"(?:(?:color|background(?:-color)?|border(?:-[a-z]+)?|outline(?:-color)?|fill|stroke|box-shadow|text-shadow|caret-color|-webkit-tap-highlight-color|-webkit-text-fill-color)\s*[:=]\s*\"?)([^;\"'>]*)", re.I)
hits, kw = [], []
for n, line in enumerate(src.split("\n"), 1):
    for m in ctx.finditer(line):
        val = m.group(1)
        for w in re.findall(r"[A-Za-z]+", val):
            if w.lower() in NAMED:
                hits.append(f"{n}: {w}  <- {line.strip()[:110]}")
            elif w in KEYWORDS:
                kw.append(f"{n}: {w}")
print("named colours:", len(hits))
print("\n".join(hits) if hits else "  (none)")
print("keywords (not colours: no hue of their own):", len(kw))
print("\n".join(sorted(set(kw), key=lambda s: int(s.split(':')[0]))))

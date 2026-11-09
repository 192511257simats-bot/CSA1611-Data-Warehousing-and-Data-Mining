"""Render source code and real program output as screenshot-style PNGs (title bar + monospace text)."""
import json, glob, os
from PIL import Image, ImageDraw, ImageFont
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SZ, WRAP, LINES = 15, 112, 58
f = ImageFont.truetype(FONT, SZ); fb = ImageFont.truetype(FB, SZ-1); cw = f.getlength("M"); lh = SZ + 6
def wrap(lines):
    out = []
    for l in lines:
        l = l.expandtabs(4).rstrip()
        first = True
        while len(l) > WRAP:
            out.append(l[:WRAP] if first else "      " + l[:WRAP-6]); l = l[WRAP:] if first else l[WRAP-6:]; first = False
        out.append(l if first else "      " + l)
    return out
def draw(lines, title, dark, numbers, start=1, path="x.png"):
    bg, fg, bar, nc = ((30, 32, 38), (220, 222, 228), (50, 53, 62), (110, 115, 128)) if dark else ((250, 250, 250), (30, 30, 30), (225, 227, 232), (150, 150, 150))
    gut = 5*cw if numbers else 0; W = int(WRAP*cw + gut + 40); H = 38 + len(lines)*lh + 24
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 38], fill=bar)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse([14+i*22, 12, 26+i*22, 24], fill=c)
    d.text((100, 9), title, font=fb, fill=fg)
    for i, l in enumerate(lines):
        y = 48 + i*lh
        if numbers and not l.startswith("      "): d.text((12, y), f"{start+i:>3}", font=f, fill=nc)
        d.text((20+gut, y), l, font=f, fill=fg)
    im.save(path); return im.size
man = {}
def run(src, kind, title, dark, numbers, key):
    lines = wrap(open(src).read().splitlines()); n = 0; man[key] = []
    for i in range(0, len(lines), LINES):
        n += 1; p = f"shots/{key}_{n}.png"; chunk = lines[i:i+LINES]
        sz = draw(chunk, f"{title}  (part {n})" if len(lines) > LINES else title, dark, numbers, i+1, p); man[key].append({"path": p, "w": sz[0], "h": sz[1]})
for q in range(1, 8):
    name = glob.glob(f"q{q}_*.py")[0]
    run(name, "code", f"{name} - source code", False, True, f"q{q}_code")
    run(f"out/q{q}.txt", "out", f"$ python3 {name}   (program output)", True, False, f"q{q}_out")
run("common.py", "code", "common.py - shared helpers", False, True, "common_code")
json.dump(man, open("shots/manifest.json", "w"), indent=1)
print({k: len(v) for k, v in man.items()})

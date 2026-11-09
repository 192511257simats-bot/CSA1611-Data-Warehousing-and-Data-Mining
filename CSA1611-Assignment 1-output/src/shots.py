"""shots.py - renders program source and program output as terminal-style PNG screenshots (img/)."""
import sys, textwrap, os
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
def render(lines, title, out, cmd=None, wrap=98):
    L = []
    if cmd: L.append(("$ " + cmd, "cmd"))
    for ln in lines:
        w = textwrap.wrap(ln.expandtabs(4), wrap, drop_whitespace=False, replace_whitespace=False) or [""]
        L += [(x if i == 0 else "   " + x, "txt") for i, x in enumerate(w)]
    cw = F.getlength("M"); W = int(cw * (wrap + 6)); H = 44 + 22 * len(L) + 16
    im = Image.new("RGB", (W, H), "#1e1e1e"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 30], fill="#3c3c3c"); [d.ellipse([10 + i * 20, 9, 22 + i * 20, 21], fill=c) for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f"))]
    d.text((W // 2 - len(title) * 4, 6), title, fill="#dddddd", font=F)
    for i, (t, k) in enumerate(L): d.text((14, 40 + i * 22), t, fill="#7ee787" if k == "cmd" else ("#9cdcfe" if "PASS" in t else "#e6e6e6"), font=FB if k == "cmd" else F)
    im.save(out)
def code(path, per=44, prefix=None):
    src = open(path).read().splitlines(); name = os.path.basename(path); prefix = prefix or name.replace(".py", "")
    n = (len(src) + per - 1) // per; outs = []
    for i in range(n):
        o = f"img/code_{prefix}_{i+1}.png"; render([f"{j+1:3d}  {t}" for j, t in enumerate(src[i * per:(i + 1) * per], i * per)], f"{name}  (part {i+1}/{n})", o); outs.append(o)
    return outs
def output(txt, title, cmd, out, maxl=70, wrap=98):
    lines = open(txt).read().splitlines()[:maxl]; render(lines, title, out, cmd, wrap)
if __name__ == "__main__":
    for p in ("build_db.py", "bench.py", "olap_app.py", "etl_task5.py", "day4.py", "task4_calc.py", "task6_lattice.py", "knime_equivalent.py", "bench_report.py"): print(p, code(p))
    output("out/etl_task5_output.txt", "Terminal - etl_task5.py", "python etl_task5.py", "img/out_etl.png", 60, 150)
    output("out/task4_calc.txt", "Terminal - task4_calc.py", "python task4_calc.py", "img/out_task4.png", 70, 130)
    output("out/task6_lattice.txt", "Terminal - task6_lattice.py", "python task6_lattice.py", "img/out_lattice.png", 70, 120)
    for n in ("rollup", "drilldown", "slice", "dice", "pivot", "boundary", "1m"):
        db = "fc_1000000.db" if n == "1m" else "fc_100000.db"; output(f"out/olap_{n}.txt", f"Terminal - OLAP app ({n})", f"python olap_app.py {db}", f"img/out_olap_{n}.png", 80)
    output("out/bench_report.txt", "Terminal - bench_report.py", "python bench_report.py", "img/out_bench.png", 75, 150)
    output("out/day4_output.txt", "Terminal - day4.py", "python day4.py fc_1000000.db", "img/out_day4.png", 60, 120)
    output("out/knime_equiv_output.txt", "Terminal - knime_equivalent.py", "python knime_equivalent.py", "img/out_knime.png", 70, 105)

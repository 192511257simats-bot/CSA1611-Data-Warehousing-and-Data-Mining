"""Render console outputs (out/*.txt) to terminal-style PNG screenshots + architecture diagram."""
from PIL import Image, ImageDraw, ImageFont
import glob, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
for f in glob.glob("../out/q*.txt"):
    lines = open(f).read().rstrip().split("\n")
    w = max(len(l) for l in lines)*13+60; h = len(lines)*30+70
    im = Image.new("RGB", (w, h), "#1e1e1e"); d = ImageDraw.Draw(im)
    d.rectangle([0,0,w,38], fill="#3c3c3c")
    for i,c in enumerate(["#ff5f56","#ffbd2e","#27c93f"]): d.ellipse([14+i*26,12,28+i*26,26], fill=c)
    d.text((110,7), "python3 "+os.path.basename(f).replace(".txt",".py"), font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",18), fill="#cccccc")
    for i,l in enumerate(lines): d.text((24,56+i*30), l, font=font, fill="#d4d4d4")
    im.save(f.replace(".txt","_screenshot.png"))

# architecture diagram
fig, ax = plt.subplots(figsize=(10,6.2)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(-0.3,7)
def box(x,y,w,h,t,c): 
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.05",fc=c,ec="#333")); ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=8.5)
def arr(a,b): ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="<->",color="#333"))
box(0.2,5.6,9.6,1.1,"USER INTERFACE  - query/task specification, visualisation of patterns\n(R8: user interaction, privacy-aware access, role-based views, interactive refinement)","#fde0dd")
box(0.2,4.1,9.6,1.0,"PATTERN-EVALUATION MODULE - interestingness thresholds (support, lift, recall on readmitted), validation\n(R7: overfitting / class imbalance check, clinician review)","#fcc5c0")
box(0.2,2.6,5.3,1.1,"DATA MINING ENGINE - classification, association,\nclustering, outlier modules (R5: scalable algorithms,\nsampling / parallel execution)","#fa9fb5")
box(5.9,2.6,3.9,1.1,"KNOWLEDGE BASE - clinical domain knowledge,\nICD hierarchies, thresholds, user beliefs (R3)","#f768a1")
box(0.2,1.2,9.6,0.9,"DATABASE / DATA WAREHOUSE SERVER - cleaning, integration, selection; fetches task-relevant data\n(R1: missing lab values, R2: patient-ID matching, R4: mixed data types, R6: de-identification)","#c7e9b4")
box(0.2,0.0,2.2,0.8,"Admission DB","#edf8b1"); box(2.6,0.0,2.2,0.8,"Laboratory DB","#edf8b1"); box(5.0,0.0,2.2,0.8,"Pharmacy DB","#edf8b1"); box(7.4,0.0,2.4,0.8,"Billing DB","#edf8b1")
for y0,y1 in [(5.6,5.1),(4.1,3.7),(2.6,2.1),(1.2,0.8)]: arr((5,y0),(5,y1))
arr((5.5,3.15),(5.9,3.15))
ax.set_title("Fig. 2.1  Architecture of the MediCore data mining system", fontsize=11)
plt.tight_layout(); plt.savefig("../out/q2_architecture.png", dpi=200)

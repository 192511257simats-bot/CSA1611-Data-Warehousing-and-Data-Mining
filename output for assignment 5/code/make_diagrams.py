import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
NAVY="#1f4e79"; LIGHT="#e8f0f8"; ORG="#e67e22"; ORGL="#fdebd0"; GRY="#555"
def box(ax,x,y,w,h,txt,fc=LIGHT,ec=NAVY,fs=8.5,bold=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.08",fc=fc,ec=ec,lw=1.4))
    ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=fs,fontweight="bold" if bold else "normal",wrap=True)
def arr(ax,x1,y1,x2,y2,c=NAVY): ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=12,lw=1.3,color=c))
def arch(revised,fn):
    fig,ax=plt.subplots(figsize=(15,7.4)); ax.set_xlim(0,15); ax.set_ylim(0,7.4); ax.axis("off")
    for x,t in [(0.1,"1 DATA SOURCES"),(2.9,"2 ETL / STAGING"),(6.5,"3 WAREHOUSE & STORES"),(9.2,"4 MINING MODULES"),(12.2,"5 REPORTING")]: ax.text(x,7.1,t,fontsize=10,fontweight="bold",color=NAVY)
    fc=lambda ch:(ORGL if (revised and ch) else LIGHT); ec=lambda ch:(ORG if (revised and ch) else NAVY)
    R=revised
    S=[("Complaints: app, portal, social\n"+("EN + Tamil + Hindi\n20,000 / day" if R else "free text\n5,000 / day"),True),("Web portal logs\n+ linked news pages",False),("Incident GPS records\n(accidents, hazards)",True),("Operational DB\n(completed requests)",True)]
    ys=[5.5,3.9,2.3,0.7]
    for y,(t,ch) in zip(ys,S): box(ax,0.1,y,2.4,1.3,t,fc(ch),ec(ch),8.5)
    E=[("TEXT ETL\nclean"+(" > language-detect\n> per-language tokenise\n" if R else "\n")+"> stop/stem > TF-IDF index",True),("WEB ETL\ncrawl, strip tags + boilerplate,\nsessionise logs",False),("SPATIAL ETL\n"+("exact GPS > 250 m grid cell\nat ETL; raw GPS dropped" if R else "validate GPS,\nload as points"),True),("RELATIONAL ETL\n"+("drop name / phone / address;\nkeyed pseudonym" if R else "surrogate keys,\nslowly-changing dims"),True)]
    for y,(t,ch) in zip(ys,E): box(ax,2.9,y,3.2,1.3,t,fc(ch),ec(ch),8)
    for y in ys: arr(ax,2.5,y+.65,2.9,y+.65)
    box(ax,6.5,4.6,2.3,2.2,"STAR SCHEMA\nFact_ServiceRequest\nDim_Time, Dim_Location\n"+("(ward>zone>grid cell)" if R else "(ward>street>GPS)")+"\nDim_Category, Dim_Dept\nDim_Channel"+(", Dim_Language" if R else ""),fc(True),ec(True),8,True)
    box(ax,6.5,2.6,2.3,1.5,"Text store / index\nTF-IDF vectors, topics",fc(True),ec(True),8.5)
    box(ax,6.5,0.7,2.3,1.5,"Spatial store\npoints, grid cells, polygons",fc(True),ec(True),8.5)
    arr(ax,6.1,6.15,6.5,5.9); arr(ax,6.1,4.55,6.5,5.2); arr(ax,6.1,2.95,6.5,3.4); arr(ax,6.1,1.35,6.5,1.5)
    M=[("TEXT MINING\nretrieval, topic + urgency\nclassifier, k-means\n"+("multilingual features" if R else "English TF-IDF"),True,4.6),("WEB MINING\nPageRank / HITS, usage\npatterns, page classifier",False,2.6),("SPATIAL MINING\nDBSCAN hot-spots,\nco-location (A,B,C)"+("\non grid cells" if R else ""),True,0.7)]
    for t,ch,y in M: box(ax,9.2,y,2.6,1.7,t,fc(ch),ec(ch),8)
    arr(ax,8.8,5.7,9.2,5.5); arr(ax,8.8,3.3,9.2,3.4); arr(ax,8.8,1.5,9.2,1.5); arr(ax,8.8,5.0,9.2,3.9)
    box(ax,12.2,3.4,2.6,3.4,"REPORTING LAYER\nOLAP summary reports\nDashboards, hot-spot maps\nUrgent-topic alerts\n"+("small-cell suppression (k>=5)" if R else "role-based access"),fc(True),ec(True),8.5,True)
    for y in (5.45,3.45,1.55): arr(ax,11.8,y,12.2,min(max(y,3.9),6.2))
    box(ax,12.2,0.7,2.6,2.2,"PRIVACY & GOVERNANCE\nconsent log, k-anonymity,\naudit, retention policy\n"+("pseudonym key vault\n(kept outside platform)" if R else ""),ORGL if R else LIGHT,ORG if R else NAVY,8)
    ax.text(7.5,0.2,("Orange = parts changed / added for Task 9 (data-protection rule, 3 languages, 20,000 complaints/day)" if R else "Original design (Task 8): privacy controls applied at the reporting layer"),ha="center",fontsize=9.5,color=GRY)
    fig.tight_layout(); fig.savefig(fn,dpi=200); plt.close()
arch(False,"../figs/fig_architecture.png"); arch(True,"../figs/fig_architecture_revised.png")
# pipeline diagram (Task 4)
fig,ax=plt.subplots(figsize=(13,2.8)); ax.set_xlim(0,13); ax.set_ylim(0,2.8); ax.axis("off")
st=[("1 Collect","crawler: portal pages,\nlinked news URLs"),("2 Clean","strip tags/scripts,\nremove nav/ads\n(boilerplate)"),("3 Features","title, headings, URL\ntokens, anchor text,\nneighbour-page labels"),("4 Train","TF-IDF + Naive Bayes /\nlinear SVM; labelled\nsample (6 classes)"),("5 Evaluate","hold-out + CV, per-class\nP/R/F1, confusion matrix"),("6 Deploy","batch classify new pages,\nconfidence threshold →\nhuman review; monitor")]
for i,(a,b) in enumerate(st):
    x=0.15+i*2.15; box(ax,x,0.5,1.85,1.8,"",LIGHT,NAVY); ax.text(x+.92,2.0,a,ha="center",fontweight="bold",color=NAVY,fontsize=10); ax.text(x+.92,1.2,b,ha="center",va="center",fontsize=7.8)
    if i<5: arr(ax,x+1.85,1.4,x+2.15,1.4)
ax.text(6.5,0.15,"Feedback loop: drift monitor (accuracy / class mix / new vocabulary) triggers retraining",ha="center",fontsize=9,color=ORG)
fig.tight_layout(); fig.savefig("../figs/fig_web_pipeline.png",dpi=200); plt.close()
# link graph (Task 3)
fig,ax=plt.subplots(figsize=(5.4,3.6)); ax.set_xlim(0,6); ax.set_ylim(0,4); ax.axis("off")
pos={"H":(1.2,2.8),"S":(3.0,3.5),"C":(3.0,1.6),"N":(5.0,2.0),"A":(5.0,0.5)}
for n,(x,y) in pos.items(): ax.add_patch(plt.Circle((x,y),.33,fc=LIGHT,ec=NAVY,lw=1.6)); ax.text(x,y,n,ha="center",va="center",fontweight="bold")
for a,b in [("H","S"),("H","C"),("S","C"),("C","H"),("N","H"),("N","C"),("N","A"),("A","N")]:
    (x1,y1),(x2,y2)=pos[a],pos[b]; import math; d=math.hypot(x2-x1,y2-y1); ux,uy=(x2-x1)/d,(y2-y1)/d; off=0.07 if (b,a) in [("C","H"),("A","N"),("N","A"),("H","C")] else 0
    ax.add_patch(FancyArrowPatch((x1+ux*.35-uy*off*2,y1+uy*.35+ux*off*2),(x2-ux*.35-uy*off*2,y2-uy*.35+ux*off*2),arrowstyle="-|>",mutation_scale=12,lw=1.2,color=GRY))
fig.tight_layout(); fig.savefig("../figs/fig_linkgraph.png",dpi=200); plt.close()

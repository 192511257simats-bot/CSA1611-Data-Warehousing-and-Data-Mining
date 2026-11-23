"""TASK 9 (Design Challenge) - evidence experiments: (A) location generalisation vs DBSCAN hot-spots, (B) multilingual complaints vs English-only model."""
import numpy as np, pandas as pd, random, time, re, warnings; warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.metrics import adjusted_rand_score, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from corpus import make_corpus, analyzer
df=pd.read_csv("../outputs/incidents.csv"); XY=df[["x_km","y_km"]].values; true=df.true_label.values
EPS=float(open("../outputs/eps.txt").read()); orig=np.load("../outputs/dbscan_labels.npy")
print("=== PART A: replace exact GPS by grid-cell centre (privacy), re-run DBSCAN (MinPts=10) ===")
print(f"{'cell size':>10} | {'eps used':>9} | clusters | noise | ARI vs truth | ARI vs original DBSCAN")
print(f"{'exact GPS':>10} | {EPS:7.3f}km |   3      | {int((orig==-1).sum()):4d}  |   {adjusted_rand_score(true,orig):.3f}      |   1.000")
fig,axs=plt.subplots(1,3,figsize=(13,4)); cols=["#1f77b4","#2ca02c","#ff7f0e","#9467bd","#8c564b","#17becf","#e377c2","#bcbd22"]
shown=0
for g in [0.1,0.25,0.5,1.0,2.0]:
    snapped=(np.floor(XY/g)+0.5)*g
    for eps in sorted({EPS, max(EPS,1.5*g)}):
        lb=DBSCAN(eps=eps,min_samples=10).fit(snapped).labels_
        print(f"{g*1000:8.0f} m | {eps:7.3f}km | {len(set(lb)-{-1}):5d}    | {int((lb==-1).sum()):4d}  |   {adjusted_rand_score(true,lb):.3f}      |   {adjusted_rand_score(orig,lb):.3f}")
        if g in (0.25,1.0) and eps!=EPS or (g==0.5 and eps!=EPS):
            pass
    if g in (0.25,0.5,1.0):
        lb=DBSCAN(eps=max(EPS,1.5*g),min_samples=10).fit(snapped).labels_
        for k in set(lb): m=lb==k; axs[shown].scatter(snapped[m,0],snapped[m,1],s=8,c="lightgrey" if k==-1 else cols[k%8],marker="x" if k==-1 else "o")
        axs[shown].set_title(f"{int(g*1000)} m grid, eps={max(EPS,1.5*g):.2f} km: {len(set(lb)-{-1})} clusters"); axs[shown].set_aspect("equal"); shown+=1
fig.tight_layout(); fig.savefig("../figs/fig_grid_effect.png",dpi=200); plt.close()

print("\n=== PART B: multilingual complaints ===")
TR={"Roads":[("pothole","गड्ढा","குழி"),("road","सड़क","சாலை"),("bridge","पुल","பாலம்"),("traffic","यातायात","போக்குவரத்து"),("signal","सिग्नल","சிக்னல்")],
"Water":[("water","पानी","தண்ணீர்"),("leak","रिसाव","கசிவு"),("pipeline","पाइपलाइन","குழாய்"),("supply","आपूर्ति","விநியோகம்"),("tank","टंकी","தொட்டி")],
"Sanitation":[("garbage","कचरा","குப்பை"),("drain","नाली","வடிகால்"),("sewage","सीवेज","கழிவுநீர்"),("dustbin","कूड़ेदान","குப்பைத்தொட்டி"),("stench","बदबू","துர்நாற்றம்")],
"Electricity":[("power","बिजली","மின்சாரம்"),("pole","खंभा","கம்பம்"),("wire","तार","கம்பி"),("transformer","ट्रांसफार्मर","மின்மாற்றி"),("outage","कटौती","துண்டிப்பு")],
"Health":[("hospital","अस्पताल","மருத்துவமனை"),("fever","बुखार","காய்ச்சல்"),("mosquito","मच्छर","கொசு"),("doctor","डॉक्टर","மருத்துவர்"),("medicine","दवा","மருந்து")]}
GEN={0:["ward","near","school","urgent","street"],1:["वार्ड","पास","स्कूल","जरूरी","गली"],2:["வார்டு","அருகில்","பள்ளி","அவசரம்","தெரு"]}
def lang_corpus(li,n=120,seed=1):
    r=random.Random(seed+li); D=[];Y=[];names=list(TR)
    for c in names:
        for _ in range(n):
            ws=[w[li] for w in r.sample(TR[c],3)]
            if r.random()<.12: ws.append(r.choice(TR[r.choice([x for x in names if x!=c])])[li])
            ws+=r.sample(GEN[li],2); r.shuffle(ws); D.append(" ".join(ws)); Y.append(c)
    return D,np.array(Y)
(en,yen),(hi,yhi),(ta,yta)=lang_corpus(0),lang_corpus(1),lang_corpus(2)
print("Sample Hindi:",hi[0],"|",yhi[0]); print("Sample Tamil:",ta[0],"|",yta[0])
w=ta[0].split()[0]; print("Tokeniser check on Tamil word",w,"-> default regex \\w\\w+ gives",re.findall(r"(?u)\b\w\w+\b",w),"(word is broken: vowel signs are not \\w)  vs whitespace tokeniser ->",w.split())
ws=lambda t:t.lower().split()
split=lambda D,Y:train_test_split(D,Y,test_size=.3,stratify=Y,random_state=42)
E=split(en,yen);H=split(hi,yhi);T=split(ta,yta)
def fit(Dtr,Ytr,clf):
    v=TfidfVectorizer(analyzer=ws); X=v.fit_transform(Dtr); m=clf().fit(X,Ytr); return v,m
ev=lambda v,m,D,Y:accuracy_score(Y,m.predict(v.transform(D)))
for cn,clf in [("NaiveBayes",MultinomialNB),("LinearSVM",lambda:LinearSVC(random_state=42))]:
    v,m=fit(E[0],E[2],clf); print(f"\n[{cn}] (1) English-only model, |V|={len(v.vocabulary_)}: acc English={ev(v,m,*E[1::2]):.3f}  Hindi={ev(v,m,*H[1::2]):.3f}  Tamil={ev(v,m,*T[1::2]):.3f}")
    Dtr=E[0]+H[0]+T[0]; Ytr=np.concatenate([E[2],H[2],T[2]]); v,m=fit(Dtr,Ytr,clf)
    print(f"[{cn}] (2) Trilingual model trained on all three, |V|={len(v.vocabulary_)}: acc English={ev(v,m,*E[1::2]):.3f}  Hindi={ev(v,m,*H[1::2]):.3f}  Tamil={ev(v,m,*T[1::2]):.3f}")
    d={}; [d.__setitem__(x[1],x[0]) or d.__setitem__(x[2],x[0]) for c in TR for x in TR[c]]
    for li,k in [(1,"वार्ड पास स्कूल जरूरी गली"),(2,"வார்டு அருகில் பள்ளி அவசரம் தெரு")]: pass
    tr=lambda D:[" ".join(d.get(t,t) for t in s.split()) for s in D]
    v,m=fit(E[0],E[2],clf); print(f"[{cn}] (3) Pivot-to-English (dictionary stands in for machine translation): acc Hindi={ev(v,m,tr(H[1]),H[3]):.3f}  Tamil={ev(v,m,tr(T[1]),T[3]):.3f}")
# throughput for 20,000 complaints/day
docs,y,_=make_corpus(120,42); v=TfidfVectorizer(analyzer=analyzer(True,True)); X=v.fit_transform(docs); m=LinearSVC(random_state=42).fit(X,y)
big=(docs*34)[:20000]; t=time.time(); m.predict(v.transform(big)); print(f"\nThroughput: vectorise+classify 20,000 complaints in {time.time()-t:.2f} s (single core)")

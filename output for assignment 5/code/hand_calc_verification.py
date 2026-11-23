"""Tool verification of the HAND calculations for Tasks 1, 3, 5, 7 (hand working is in the report)."""
import math, numpy as np
print("=== TASK 1: TF-IDF / cosine ===")
docs={"D1":"pothol main road school","D2":"garbag collect school road","D3":"street light work main road","D4":"water leakag school gate"}
q="school road garbag".split(); N=len(docs); terms=sorted({t for d in docs.values() for t in d.split()})
df={t:sum(t in d.split() for d in docs.values()) for t in terms}; idf={t:math.log10(N/df[t]) for t in terms}
print("term      df   idf");  [print(f"{t:9s}{df[t]:3d}  {idf[t]:.4f}") for t in terms]
vec=lambda toks:{t:toks.count(t)*idf.get(t,0) for t in set(toks)}
V={k:vec(v.split()) for k,v in docs.items()}; Q=vec(q)
for k,v in V.items(): print(k,{t:round(w,4) for t,w in v.items()},"|d|=%.4f"%math.sqrt(sum(w*w for w in v.values())))
print("Q",{t:round(w,4) for t,w in Q.items()},"|q|=%.4f"%math.sqrt(sum(w*w for w in Q.values())))
sc={}
for k,v in V.items():
    dot=sum(Q[t]*v.get(t,0) for t in Q); sc[k]=dot/(math.sqrt(sum(w*w for w in v.values()))*math.sqrt(sum(w*w for w in Q.values())))
    print(f"{k}: dot={dot:.4f} cos={sc[k]:.4f}")
rank=sorted(sc,key=sc.get,reverse=True); print("Ranking:",rank); rel={"D1","D2"}
tp=len(set(rank[:2])&rel); print(f"P@2={tp/2:.2f}  R@2={tp/len(rel):.2f}")
print("\n=== TASK 3: PageRank (d=0.85, PR0=0.2, synchronous updates) ===")
out={"H":["S","C"],"S":["C"],"C":["H"],"N":["H","C","A"],"A":["N"]}; pr={p:.2 for p in out}
for it in (1,2):
    new={p:0.15/5+0.85*sum(pr[q]/len(out[q]) for q in out if p in out[q]) for p in out}; pr=new
    print(f"iter {it}:",{p:round(v,4) for p,v in pr.items()},"sum=%.4f"%sum(pr.values()))
print("\n=== TASK 5: co-location participation index ===")
A,B,C=4,5,3
pairs={"A-B":[("A1","B1"),("A1","B2"),("A2","B2"),("A3","B4")],"A-C":[("A1","C1"),("A2","C1"),("A3","C2")],"B-C":[("B1","C1"),("B2","C1")]}
tot={"A":4,"B":5,"C":3}
for k,p in pairs.items():
    f1,f2=k.split("-"); a=len({x[0] for x in p}); b=len({x[1] for x in p}); pr1,pr2=a/tot[f1],b/tot[f2]
    print(f"{k}: PR({f1})={a}/{tot[f1]}={pr1:.3f}  PR({f2})={b}/{tot[f2]}={pr2:.3f}  PI={min(pr1,pr2):.3f}  prevalent(>=0.5)={min(pr1,pr2)>=.5}")
tri=[("A1","B1","C1"),("A1","B2","C1"),("A2","B2","C1")]
r=[len({t[i] for t in tri})/n for i,n in enumerate((4,5,3))]; print("Triple ABC ratios",[round(x,3) for x in r],"PI=%.3f prevalent=%s"%(min(r),min(r)>=.5))
print("\n=== TASK 7: k-anonymity ===")
import collections
T=[(23,600041,"Garbage"),(27,600042,"Garbage"),(24,600041,"Water"),(52,600087,"Roads"),(58,600088,"Roads"),(55,600087,"Water")]
c=collections.Counter((a,p) for a,p,_ in T); print("original groups (Age,PIN):",dict(c),"=> k =",min(c.values()))
g=lambda a,p:(f"{a//10*10}-{a//10*10+9}",str(p)[:5]+"*"); c2=collections.Counter(g(a,p) for a,p,_ in T)
print("generalised groups:",dict(c2),"=> k =",min(c2.values()))
for a,p,t in T: print(g(a,p),t)

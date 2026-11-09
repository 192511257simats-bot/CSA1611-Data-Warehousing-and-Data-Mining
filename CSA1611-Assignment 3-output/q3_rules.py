"""Q3 - Tree->rules with coverage/accuracy, sequential covering, class-association rules, JRip-like learner."""
import itertools, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from common import *

df = loan12(); A = ["Income", "Credit", "Employment"]; N = len(df)
def match(d, conds): 
    m = pd.Series(True, index=d.index)
    for a, v in conds: m &= d[a] == v
    return m
print("=== Student A: rules from the Q1 tree, coverage and accuracy on the 12 tuples ===")
print(f"{'Rule':<4} {'Condition':<60} {'Class':<5} {'Cover':>6} {'Cov%':>6} {'Acc':>6}")
for i, (p, lab) in enumerate(paths(id3(df, A)), 1):
    m = match(df, p); cov = int(m.sum()); ok = int((df[m].Approved == lab).sum())
    cond = " AND ".join(f"{a}={v}" for a, v in p)
    print(f"R{i:<3} {cond:<60} {lab:<5} {cov:>3}/12 {100*cov/N:>5.1f}% {('n/a' if cov==0 else f'{ok}/{cov}'):>6}")

print("\n=== Sequential covering (learn one rule, remove covered tuples, repeat) for class Yes ===")
items = [(a, v) for a in A for v in sorted(df[a].unique())]
rest = df.copy(); k = 0
while (rest.Approved == "Yes").any() and k < 6:
    conds = []; cur = rest
    while (cur.Approved == "No").any():
        best, bg = None, 0
        for it in items:
            if it in conds: continue
            c2 = cur[match(cur, [it])]; p1 = (c2.Approved == "Yes").sum()
            if p1 == 0: continue
            p0, n0 = (cur.Approved == "Yes").sum(), len(cur)
            g = p1*(np.log2(p1/len(c2)) - np.log2(p0/n0))        # FOIL gain
            if g > bg: best, bg = it, g
        if best is None: break
        conds.append(best); cur = cur[match(cur, [best])]
    k += 1; cov = match(rest, conds); 
    print(f"Rule {k}: IF {' AND '.join(f'{a}={v}' for a,v in conds)} THEN Yes | covers tuples {list(rest[cov].index)} "
          f"({(rest[cov].Approved=='Yes').sum()} Yes, {(rest[cov].Approved=='No').sum()} No)")
    rest = rest[~cov]; print("   tuples left after removal:", list(rest.index))

print("\n=== Student B: class-association rules (min support 25%, min confidence 70%) -> Approved=Yes ===")
print(f"{'Rule':<55} {'sup':>6} {'conf':>6}")
cars = []
for r in (1, 2, 3):
    for attrs in itertools.combinations(A, r):
        for vals in itertools.product(*[sorted(df[a].unique()) for a in attrs]):
            cond = list(zip(attrs, vals)); m = match(df, cond)
            if m.sum() == 0: continue
            both = int((df[m].Approved == "Yes").sum()); sup = both/N; conf = both/m.sum()
            if sup >= 0.25 and conf >= 0.70: cars.append((cond, both, sup, conf))
for cond, both, sup, conf in cars:
    print(f"{' AND '.join(f'{a}={v}' for a,v in cond):<45} => Yes   {both}/12={sup*100:>4.1f}% {conf*100:>5.1f}%")
print("\n=== Rule conflict example: all rules with 1-2 conditions, confidence >= 60%, either class ===")
allr = []
for r in (1, 2):
    for attrs in itertools.combinations(A, r):
        for vals in itertools.product(*[sorted(df[a].unique()) for a in attrs]):
            cond = list(zip(attrs, vals)); m = match(df, cond)
            for c in ("Yes", "No"):
                k = int((df[m].Approved == c).sum())
                if m.sum() and k/m.sum() >= 0.6 and k >= 2: allr.append((cond, c, k/m.sum(), k/N))
for t in (6, 11):
    hits = [x for x in allr if match(df.loc[[t]], x[0]).iloc[0]]
    print(f"Tuple {t} {tuple(df.loc[t,A])} actual={df.loc[t,'Approved']}: {len(hits)} rules fire")
    for cond, c, conf, sup in sorted(hits, key=lambda x: (-len(x[0]), -x[2])):
        print(f"   {len(cond)} cond  {' AND '.join(f'{a}={v}' for a,v in cond):<38} => {c:<3} conf={conf:.2f} sup={sup:.2f}")

print("\n=== credit_synth: J48-style tree rules vs sequential-covering (JRip-like) rules ===")
X, y = credit_synth(); Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=1)
t = DecisionTreeClassifier(criterion="entropy", min_samples_leaf=5, random_state=1).fit(Xtr, ytr)
print(f"Tree (J48-like): {t.get_n_leaves()} leaf-rules, test acc {t.score(Xte, yte):.3f}")
edges = {c: np.quantile(Xtr[c], [1/3, 2/3]) for c in X}
def disc(Z): return pd.DataFrame({f"{c}_{lab}": (b == i) for c in X for i, lab in enumerate(["lo", "mid", "hi"])
                                  for b in [np.digitize(Z[c], edges[c])]})
Btr, Bte = disc(Xtr), disc(Xte); yb = pd.Series(ytr, index=Btr.index); rules = []; left = Btr.copy(); yl = yb.copy()
for _ in range(12):
    conds, cur = [], np.ones(len(left), bool)
    while True:
        p0, n0 = (yl[cur] == 1).sum(), cur.sum()
        if p0 == 0 or (yl[cur] == 0).sum() == 0 or len(conds) >= 3: break
        best, bg = None, 0
        for c in left.columns:
            if c in conds: continue
            m2 = cur & left[c].values; p1 = (yl[m2] == 1).sum()
            if p1 < 8: continue
            g = p1*(np.log2(p1/m2.sum()) - np.log2(p0/n0))
            if g > bg: best, bg = c, g
        if best is None: break
        conds.append(best); cur = cur & left[best].values
    if not conds: break
    prec = (yl[cur] == 1).mean(); 
    if prec < 0.5 or cur.sum() < 10: break
    rules.append(conds); left, yl = left[~cur], yl[~cur]
print("Learned rules (class=1, minority) - default rule: class=0")
for r in rules: print("  IF", " AND ".join(r), "THEN 1")
fire = np.zeros(len(Bte), bool)
for r in rules: fire |= Bte[r].all(axis=1).values
pred = fire.astype(int); print(f"Rule list: {len(rules)} rules + default, test acc {(pred==yte).mean():.3f}, recall(class 1) {((pred==1)&(yte==1)).sum()/(yte==1).sum():.3f}")

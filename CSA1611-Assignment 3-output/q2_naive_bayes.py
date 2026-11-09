"""Q2 - Naive Bayes: manual posterior, Laplace correction, Weka-equivalent check, correlation study."""
import numpy as np, pandas as pd
from fractions import Fraction as F
from sklearn.naive_bayes import CategoricalNB, GaussianNB
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import roc_auc_score, log_loss
from common import *

df = loan12(); A = ["Income", "Credit", "Employment"]; X = {"Income": "Low", "Credit": "Good", "Employment": "Self-employed"}
def nb(data, x, k=0):
    """k = Laplace constant (0 = none). Returns exact fractions."""
    res = {}
    for c, g in data.groupby("Approved"):
        p = F(len(g), len(data)); line = [f"P({c})={p}"]
        for a in A:
            nv = data[a].nunique(); cnt = (g[a] == x[a]).sum()
            q = F(cnt + k, len(g) + k*nv); p *= q; line.append(f"P({x[a]}|{c})={q}")
        res[c] = p; print(f"  {c:3s}: " + "  ".join(line) + f"\n       posterior ~ {float(p):.5f}")
    tot = sum(res.values()); print("  normalised:", {c: round(float(v/tot), 4) for c, v in res.items()}, "-> predict", max(res, key=res.get))
    return res
print("=== Student A: X = (Income=Low, Credit=Good, Employment=Self-employed) ===")
nb(df, X)
print("\nZero-probability demo: remove tuple 12 (only 'Yes' with Poor credit) and classify X2=(Low, Poor, Self-employed)")
d11 = df.drop(12); X2 = {"Income": "Low", "Credit": "Poor", "Employment": "Self-employed"}
print(" Without correction:"); nb(d11, X2)
print(" With Laplace correction (k=1):"); nb(d11, X2, 1)

print("\n=== Student B: Weka NaiveBayes-equivalent check (sklearn CategoricalNB) ===")
enc = OrdinalEncoder().fit(df[A]); Xe = enc.transform(df[A]).astype(int)
m = CategoricalNB(alpha=1e-10).fit(Xe, df.Approved)
xq = enc.transform(pd.DataFrame([X])).astype(int)
print("classes", m.classes_, " priors", np.round(np.exp(m.class_log_prior_), 4))
print("P(class | X) by sklearn:", np.round(m.predict_proba(xq)[0], 4), "(manual: No 0.6048, Yes 0.3952)")
print("with alpha=1 (Laplace):", np.round(CategoricalNB(alpha=1).fit(Xe, df.Approved).predict_proba(xq)[0], 4))

print("\n=== Correlated attributes: Naive Bayes vs decision tree (n=3000, 6 informative Gaussian attributes) ===")
rng = np.random.default_rng(0); n = 3000; y = rng.integers(0, 2, n)
base = rng.normal(0, 1, (n, 6)) + 0.45*y[:, None]
cv = StratifiedKFold(10, shuffle=True, random_state=0)
print(f"{'copies of f1':>13} {'NB acc':>8} {'NB AUC':>8} {'NB logloss':>11} {'DT acc':>8} {'DT AUC':>8}")
for k in (0, 1, 2, 4, 8):
    Xk = np.hstack([base] + [base[:, [0]] + rng.normal(0, 0.05, (n, 1)) for _ in range(k)])
    pn = cross_val_predict(GaussianNB(), Xk, y, cv=cv, method="predict_proba")[:, 1]
    dt = DecisionTreeClassifier(max_depth=4, random_state=0)
    pd_ = cross_val_predict(dt, Xk, y, cv=cv, method="predict_proba")[:, 1]
    print(f"{k:>13} {((pn>.5)==y).mean():>8.3f} {roc_auc_score(y,pn):>8.3f} {log_loss(y,pn):>11.3f} {((pd_>.5)==y).mean():>8.3f} {roc_auc_score(y,pd_):>8.3f}")

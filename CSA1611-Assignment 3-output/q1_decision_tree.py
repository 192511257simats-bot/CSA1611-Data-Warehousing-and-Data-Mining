"""Q1 - Decision tree induction: manual ID3 maths + J48-equivalent (scikit-learn, entropy)."""
import math, time, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.datasets import load_breast_cancer
from common import *

df = loan12(); cls = "Approved"; A = ["Income", "Credit", "Employment"]
print("=== Student A: manual induction ===")
print("Class counts:", df[cls].value_counts().to_dict(), "-> Entropy(D) = %.4f" % entropy(df[cls]))
for a in A:
    print(f"\nAttribute {a}")
    for v, g in df.groupby(a):
        print(f"   {v:14s} n={len(g)} yes={(g[cls]=='Yes').sum()} no={(g[cls]=='No').sum()} H={entropy(g[cls]):.4f}")
    print(f"   Gain({a}) = {gain(df, a):.4f}")
# gain ratio & gini for Income
si = -sum(len(g)/12*math.log2(len(g)/12) for _, g in df.groupby("Income"))
print("\nIncome: SplitInfo = %.4f, GainRatio = %.4f" % (si, gain(df, "Income")/si))
gini = lambda y: 1 - sum((c/len(y))**2 for c in pd.Series(y).value_counts())
gi = gini(df[cls]) - sum(len(g)/12*gini(g[cls]) for _, g in df.groupby("Income"))
print("Gini(D)=%.4f  Gini reduction(Income)=%.4f" % (gini(df[cls]), gi))
for a in A:
    si_a = -sum(len(g)/12*math.log2(len(g)/12) for _, g in df.groupby(a))
    g_a = gini(df[cls]) - sum(len(g)/12*gini(g[cls]) for _, g in df.groupby(a))
    print(f"  {a:11s} GainRatio={gain(df,a)/si_a:.4f}  GiniReduction={g_a:.4f}")
tree = id3(df, A)
print("\nID3 tree:", tree); print("\nPaths:")
for p, lab in paths(tree): print("  IF", " AND ".join(f"{a}={v}" for a, v in p), "THEN Approved =", lab)
d2 = df.copy(); d2["CustID"] = d2.index
print("\nGain(CustomerID) = %.4f  (SplitInfo = %.4f, GainRatio = %.4f)" %
      (gain(d2, "CustID"), math.log2(12), gain(d2, "CustID")/math.log2(12)))

print("\n=== Student B: Weka J48-equivalent (sklearn DecisionTreeClassifier, entropy) ===")
Xo = pd.get_dummies(df[A]).astype(int); y = df[cls]
for msl in (1, 2):
    t = DecisionTreeClassifier(criterion="entropy", min_samples_leaf=msl, random_state=1).fit(Xo, y)
    print(f"\nmin_samples_leaf={msl}: leaves={t.get_n_leaves()} train acc={t.score(Xo,y):.3f}")
    print(export_text(t, feature_names=list(Xo.columns)))
fig, ax = plt.subplots(figsize=(9, 5))
t1 = DecisionTreeClassifier(criterion="entropy", random_state=1).fit(Xo, y)
plot_tree(t1, feature_names=list(Xo.columns), class_names=list(t1.classes_), filled=True, ax=ax, fontsize=8)
plt.savefig("figs/q1_tree_sklearn.png", dpi=150, bbox_inches="tight"); plt.close()

print("\n=== Larger data: credit_synth (1000 x 20, 70/30), stratified 70/30 hold-out ===")
X, yc = credit_synth(); Xtr, Xte, ytr, yte = train_test_split(X, yc, test_size=0.3, stratify=yc, random_state=1)
print("Pruning (ccp_alpha = analogue of J48 confidence factor -C; larger alpha = more pruning)")
print(f"{'ccp_alpha':>10} {'leaves':>7} {'depth':>6} {'train':>7} {'test':>7}")
for al in (0, 0.001, 0.003, 0.006, 0.01, 0.02, 0.05):
    t = DecisionTreeClassifier(criterion="entropy", ccp_alpha=al, random_state=1).fit(Xtr, ytr)
    print(f"{al:>10} {t.get_n_leaves():>7} {t.get_depth():>6} {t.score(Xtr,ytr):>7.3f} {t.score(Xte,yte):>7.3f}")
print("\nMinimum instances per leaf (J48 -M)")
print(f"{'minLeaf':>10} {'leaves':>7} {'depth':>6} {'train':>7} {'test':>7}")
for m in (1, 2, 5, 10, 20, 40):
    t = DecisionTreeClassifier(criterion="entropy", min_samples_leaf=m, random_state=1).fit(Xtr, ytr)
    print(f"{m:>10} {t.get_n_leaves():>7} {t.get_depth():>6} {t.score(Xtr,ytr):>7.3f} {t.score(Xte,yte):>7.3f}")
dep = list(range(1, 21)); tr, te = [], []
for d in dep:
    t = DecisionTreeClassifier(criterion="entropy", max_depth=d, random_state=1).fit(Xtr, ytr)
    tr.append(t.score(Xtr, ytr)); te.append(t.score(Xte, yte))
plt.figure(figsize=(6, 3.6)); plt.plot(dep, tr, "o-", label="training accuracy"); plt.plot(dep, te, "s-", label="test accuracy")
plt.xlabel("max tree depth"); plt.ylabel("accuracy"); plt.title("Overfitting: credit_synth"); plt.legend(); plt.grid(alpha=.3)
plt.savefig("figs/q1_overfit.png", dpi=150, bbox_inches="tight"); plt.close()
print("\nOverfitting evidence: depth=%d train=%.3f test=%.3f ; best test depth=%d (%.3f)" %
      (dep[-1], tr[-1], te[-1], dep[int(np.argmax(te))], max(te)))
bc = load_breast_cancer()
for m in (2, 10):
    s = cross_val_score(DecisionTreeClassifier(criterion="entropy", min_samples_leaf=m, random_state=1), bc.data, bc.target, cv=10)
    print(f"Real data (breast cancer, 569x30) 10-fold CV, min_samples_leaf={m}: {s.mean():.3f}")

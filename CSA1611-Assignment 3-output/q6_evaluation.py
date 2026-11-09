"""Q6 - Metrics, error measures, estimation methods (holdout / 10-fold CV / .632 bootstrap), paired comparison, ROC."""
import numpy as np, pandas as pd, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, RepeatedStratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.base import clone
from common import credit_synth
warnings.filterwarnings("ignore")
print("=== Student A: confusion-matrix metrics (TP=40 FN=20 FP=30 TN=910) ===")
TP, FN, FP, TN = 40, 20, 30, 910; n = TP+FN+FP+TN
acc = (TP+TN)/n; rec = TP/(TP+FN); spec = TN/(TN+FP); prec = TP/(TP+FP); f1 = 2*prec*rec/(prec+rec)
print(f"accuracy={acc:.4f} error={1-acc:.4f} sensitivity(recall)={rec:.4f} specificity={spec:.4f} precision={prec:.4f} F1={f1:.4f}")
print(f"F2 (recall-weighted) = {5*prec*rec/(4*prec+rec):.4f}")
print(f"Always-'not fraud': accuracy={(FP+TN)/n:.3f}  recall=0.000  (misses all {TP+FN} frauds)")
a = np.array([12, 15, 20, 25.]); p = np.array([10, 18, 19, 30.]); e = p - a
print(f"errors={e.tolist()}  MAE={np.abs(e).mean():.4f}  MSE={(e**2).mean():.4f}  RMSE={np.sqrt((e**2).mean()):.4f}")
print(f"if last prediction were 50 instead of 30: MAE={np.abs([-2,3,-1,25]).mean():.3f} RMSE={np.sqrt(np.mean(np.square([-2,3,-1,25]))):.3f}")

print("\n=== Student B: estimation methods on credit_synth (1000 rows, 30% positive) ===")
X, y = credit_synth(); X = X.values
J48 = DecisionTreeClassifier(criterion="entropy", min_samples_leaf=2, random_state=1)
NBc = GaussianNB(); SMO = make_pipeline(StandardScaler(), SVC(kernel="linear", probability=True, random_state=1))
cv10 = StratifiedKFold(10, shuffle=True, random_state=1)
def boot632(model, B=100, seed=1):
    rng = np.random.default_rng(seed); accs = []
    for _ in range(B):
        idx = rng.integers(0, len(y), len(y)); oob = np.setdiff1d(np.arange(len(y)), idx)
        m = clone(model).fit(X[idx], y[idx]); accs.append(0.632*m.score(X[oob], y[oob]) + 0.368*m.score(X, y))
    return np.mean(accs)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=1/3, stratify=y, random_state=1)
print(f"{'method':<28} {'J48-like':>9} {'NaiveBayes':>11} {'SMO(linear)':>12}")
rows = {"Holdout 2/3 - 1/3 (seed 1)": [clone(m).fit(Xtr, ytr).score(Xte, yte) for m in (J48, NBc, SMO)],
        "10-fold CV": [cross_val_score(m, X, y, cv=cv10).mean() for m in (J48, NBc, SMO)],
        "Bootstrap .632 (B=100)": [boot632(m) for m in (J48, NBc, SMO)],
        "Resubstitution (training)": [clone(m).fit(X, y).score(X, y) for m in (J48, NBc, SMO)]}
for k, v in rows.items(): print(f"{k:<28} {v[0]:>9.3f} {v[1]:>11.3f} {v[2]:>12.3f}")
print("\nHoldout repeated with 8 random 2/3-1/3 splits:")
acc8 = {nm: [] for nm in ("J48", "NB", "SMO")}
for s in range(8):
    a_, b_, c_, d_ = train_test_split(X, y, test_size=1/3, stratify=y, random_state=100+s)
    for nm, m in zip(acc8, (J48, NBc, SMO)): acc8[nm].append(clone(m).fit(a_, c_).score(b_, d_))
for nm, v in acc8.items(): print(f"  {nm:<4} " + " ".join(f"{x:.3f}" for x in v) + f"  | mean {np.mean(v):.3f} sd {np.std(v, ddof=1):.3f} range {min(v):.3f}-{max(v):.3f}")

print("\n=== Paired comparison: 10 x 10-fold CV, corrected resampled t-test (Weka Experimenter style) ===")
rcv = RepeatedStratifiedKFold(n_splits=10, n_repeats=10, random_state=7)
sc = {nm: cross_val_score(m, X, y, cv=rcv) for nm, m in (("J48", J48), ("NB", NBc), ("SMO", SMO))}
for nm, v in sc.items(): print(f"  {nm:<4} mean acc {v.mean():.4f}  sd {v.std(ddof=1):.4f}")
def corr_t(a, b, n_test_over_train=1/9):
    d = a - b; k = len(d); t = d.mean()/np.sqrt((1/k + n_test_over_train)*d.var(ddof=1)); return t, 2*stats.t.sf(abs(t), k-1)
for a_, b_ in (("NB", "J48"), ("SMO", "J48"), ("SMO", "NB")):
    t, pv = corr_t(sc[a_], sc[b_]); print(f"  {a_:>3} vs {b_:<3}: mean diff {np.mean(sc[a_]-sc[b_]):+.4f}  t={t:+.2f}  p={pv:.4f}  -> {'significant' if pv<0.05 else 'not significant'} at 5%")

pr = {nm: cross_val_predict(m, X, y, cv=cv10, method="predict_proba")[:, 1] for nm, m in (("J48-like", J48), ("Naive Bayes", NBc), ("SMO (linear)", SMO))}
plt.figure(figsize=(5, 4.4))
for nm, s in pr.items():
    fpr, tpr, _ = roc_curve(y, s); plt.plot(fpr, tpr, label=f"{nm} AUC={roc_auc_score(y, s):.3f}")
plt.plot([0, 1], [0, 1], "k--", lw=.8, label="random"); plt.xlabel("False positive rate (1 - specificity)"); plt.ylabel("True positive rate (recall)")
plt.title("ROC curves, 10-fold CV, credit_synth"); plt.legend(loc="lower right", fontsize=8); plt.grid(alpha=.3)
plt.savefig("figs/q6_roc.png", dpi=150, bbox_inches="tight"); plt.close()
for nm, s in pr.items(): print(f"  AUC {nm:<13}= {roc_auc_score(y, s):.3f}")
print(f"\nMajority-class baseline accuracy = {1-y.mean():.3f}")
for nm, s in pr.items():
    pl = (s >= .5).astype(int); print(f"  {nm:<13} accuracy {np.mean(pl==y):.3f}  recall(class 1) {np.mean(pl[y==1]==1):.3f}  precision {np.mean(y[pl==1]==1):.3f}")

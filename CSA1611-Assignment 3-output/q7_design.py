"""Q7 - Day-4 design challenge: 30-day readmission (6% positive, FN costs 10x FP, missing values, explainable)."""
import numpy as np, pandas as pd, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, confusion_matrix, precision_score, recall_score
from sklearn.base import clone
warnings.filterwarnings("ignore")
C_FN, C_FP = 10, 1
print("=== Student A: analytical validation (1,000 patients, 6% readmitted = 60 positives, 940 negatives) ===")
print(f"Bayes-optimal rule: flag if P(readmit) >= C_FP/(C_FP+C_FN) = {C_FP}/{C_FP+C_FN} = {C_FP/(C_FP+C_FN):.3f}")
for name, (TP, FN, FP, TN) in {"T=0.50 (default)": (18, 42, 8, 932), "T=0.09 (cost-based)": (45, 15, 230, 710)}.items():
    cost = C_FN*FN + C_FP*FP
    print(f"{name:<22} TP={TP} FN={FN} FP={FP} TN={TN} | acc={(TP+TN)/1000:.3f} recall={TP/60:.2f} precision={TP/(TP+FP):.2f} | cost = {C_FN}x{FN} + {C_FP}x{FP} = {cost}")
print("Flag-nobody: accuracy=0.940, cost = 10x60 = 600 ; flag-everybody: accuracy=0.060, cost = 940")

print("\n=== Student B: experimental validation on a synthetic readmission-like data set ===")
rng = np.random.default_rng(7); n = 8000
d = pd.DataFrame({"age": rng.normal(65, 14, n).clip(18, 98), "diag_group": rng.choice(["cardiac", "resp", "diabetes", "ortho", "other"], n, p=[.25, .2, .2, .15, .2]),
                  "los_days": rng.gamma(2.2, 2.4, n), "prior_adm": rng.poisson(1.2, n), "lab_creat": rng.normal(1.1, .4, n), "lab_sodium": rng.normal(138, 4, n), "n_meds": rng.poisson(5, n)})
z = (-4.45 + .025*(d.age-65) + .09*d.los_days + .45*d.prior_adm + .8*(d.lab_creat-1.1) - .06*(d.lab_sodium-138) + .06*d.n_meds + (d.diag_group == "cardiac")*.6 + (d.diag_group == "resp")*.4)
y = (rng.random(n) < 1/(1+np.exp(-z))).astype(int)
for c in ("lab_creat", "lab_sodium", "n_meds"): d.loc[rng.random(n) < .12, c] = np.nan
print(f"rows={n}  readmission rate={y.mean():.3%}  missing: " + ", ".join(f"{c} {d[c].isna().mean():.0%}" for c in ('lab_creat','lab_sodium','n_meds')))
num = ["age", "los_days", "prior_adm", "lab_creat", "lab_sodium", "n_meds"]
pre = ColumnTransformer([("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), num), ("cat", OneHotEncoder(), ["diag_group"])])
treeprep = ColumnTransformer([("num", SimpleImputer(strategy="median", add_indicator=True), num), ("cat", OneHotEncoder(), ["diag_group"])])
models = {"Baseline: decision tree, depth 6, no cost handling": make_pipeline(treeprep, DecisionTreeClassifier(max_depth=6, random_state=0)),
          "Logistic regression, no imbalance handling": make_pipeline(pre, LogisticRegression(max_iter=1000)),
          "FINAL: cost-sensitive logistic regression (class_weight 10:1)": make_pipeline(pre, LogisticRegression(max_iter=1000, class_weight={0: 1, 1: 10})),
          "Cost-sensitive shallow tree (depth 3, class_weight 10:1)": make_pipeline(treeprep, DecisionTreeClassifier(max_depth=3, class_weight={0: 1, 1: 10}, random_state=0))}
cv = StratifiedKFold(10, shuffle=True, random_state=0); T = C_FP/(C_FP+C_FN); res = {}
def cost(yt, pr): tn, fp, fn, tp = confusion_matrix(yt, pr).ravel(); return C_FN*fn + C_FP*fp, tp, fn, fp, tn
print(f"\n{'model':<62} {'thr':>5} {'recall':>7} {'prec':>6} {'AUC':>6} {'cost':>6}")
for nm, m in models.items():
    p = cross_val_predict(m, d, y, cv=cv, method="predict_proba")[:, 1]; res[nm] = p
    for thr in ((0.5,) if "class_weight" in nm else (0.5, T)):
        pl = (p >= thr).astype(int); c = cost(y, pl)[0]
        print(f"{nm:<62} {thr:>5.2f} {recall_score(y,pl):>7.3f} {precision_score(y,pl,zero_division=0):>6.3f} {roc_auc_score(y,p):>6.3f} {c:>6}")
print(f"{'Flag nobody (accuracy {:.3f})'.format(1-y.mean()):<62} {'-':>5} {0:>7.3f} {'-':>6} {0.5:>6.3f} {C_FN*y.sum():>6}")
print("\nImbalance handling inside the 10 folds (logistic regression, threshold 0.5 and cost-based 0.091)")
def cv_oversample(m, factor=None):
    p = np.zeros(n)
    for tr, te in cv.split(d, y):
        idx = tr
        if factor: pos = tr[y[tr] == 1]; idx = np.concatenate([tr, rng.choice(pos, len(pos)*(factor-1))])
        p[te] = clone(m).fit(d.iloc[idx], y[idx]).predict_proba(d.iloc[te])[:, 1]
    return p
for nm, p, ts_ in (("none", res["Logistic regression, no imbalance handling"], (0.5, T)), ("class weight 10:1", res["FINAL: cost-sensitive logistic regression (class_weight 10:1)"], (0.5,)),
              ("random oversampling x10 (odds x10)", cv_oversample(models["Logistic regression, no imbalance handling"], 10), (0.5,))):
    print(f"  {nm:<36}: " + " | ".join(f"thr {t:.3f}: recall {recall_score(y,(p>=t).astype(int)):.3f} prec {precision_score(y,(p>=t).astype(int),zero_division=0):.3f} cost {cost(y,(p>=t).astype(int))[0]}" for t in ts_))
p = res["Logistic regression, no imbalance handling"]; ts = np.linspace(0.02, 0.6, 59)
cs = [cost(y, (p >= t).astype(int))[0] for t in ts]; print(f"\nCost-minimising threshold on CV probabilities of plain logistic regression: {ts[int(np.argmin(cs))]:.2f} (cost {min(cs)}); theory 1/11 = {T:.3f}")
plt.figure(figsize=(5.5, 3.6)); plt.plot(ts, cs); plt.axvline(T, ls="--", c="k"); plt.xlabel("decision threshold"); plt.ylabel("total cost (10*FN + FP)"); plt.title("Cost vs threshold (10-fold CV)"); plt.grid(alpha=.3)
plt.savefig("figs/q7_cost.png", dpi=150, bbox_inches="tight"); plt.close()
fin = models["FINAL: cost-sensitive logistic regression (class_weight 10:1)"].fit(d, y)
names = list(fin[0].get_feature_names_out()); coef = fin[-1].coef_[0]
print("\nFinal model - standardised coefficients (odds-ratio per 1 SD) for the doctor-facing explanation:")
for nm_, c_ in sorted(zip(names, coef), key=lambda t: -abs(t[1]))[:8]: print(f"  {nm_:<28} coef {c_:+.3f}  odds x{np.exp(c_):.2f}")

"""Q7 - Loan-default pipeline: ORIGINAL (flawed) vs REDESIGNED. Python / scikit-learn.
Dataset: synthetic credit data (3% defaults, 18% missing occupation, skewed income) because the
UCI German Credit file could not be downloaded in the offline workspace.  If 'german.csv' exists
next to this script the loader below can be adapted; the pipelines themselves are dataset-agnostic."""
import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import skew
from sklearn.model_selection import train_test_split, cross_val_predict, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder, KBinsDiscretizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, recall_score, precision_score, f1_score,
                             roc_auc_score, average_precision_score, confusion_matrix)
SEED = 42; rng = np.random.default_rng(SEED)

# ---------------- 1. data generation ----------------
n = 20000
age = rng.integers(21, 70, n)
income = rng.lognormal(10.6, 0.7, n)                       # right-skewed
debt_ratio = rng.beta(2, 5, n)
late = rng.poisson(0.6, n)
loan = rng.lognormal(11.0, 0.5, n)
occ = rng.choice(["Salaried", "Self-employed", "Business", "Student", "Retired"], n, p=[.45,.2,.15,.1,.1])
occ_risk = pd.Series(occ).map({"Salaried":0,"Self-employed":.6,"Business":.4,"Student":1.0,"Retired":-.3}).values
z = -9.2 + 3.0*debt_ratio + .55*late + occ_risk + .9*(loan/income) - .0000004*income - .015*(age-21)
prob = 1/(1+np.exp(-z)); prob *= 0.03/prob.mean()
y = (rng.random(n) < np.clip(prob, 0, 1)).astype(int)
df = pd.DataFrame(dict(age=age, income=income, debt_ratio=debt_ratio, late_payments=late, loan_amount=loan, occupation=occ, default=y))
miss_occ = rng.random(n) < 0.18; df.loc[miss_occ, "occupation"] = np.nan
miss_inc = rng.random(n) < np.where(y==1, 0.30, 0.08); df.loc[miss_inc, "income"] = np.nan   # missingness is informative
print(f"rows={n}  default rate={y.mean():.3%}  missing income={df.income.isna().mean():.1%}  missing occupation={df.occupation.isna().mean():.1%}")
df.to_csv("../out/loan_data.csv", index=False)
num = ["age","income","debt_ratio","late_payments","loan_amount"]

def report(name, ytrue, pred, proba):
    tn, fp, fn, tp = confusion_matrix(ytrue, pred).ravel()
    r = dict(Pipeline=name, Accuracy=accuracy_score(ytrue,pred), Precision=precision_score(ytrue,pred,zero_division=0),
             Recall=recall_score(ytrue,pred), F1=f1_score(ytrue,pred), ROC_AUC=roc_auc_score(ytrue,proba),
             PR_AUC=average_precision_score(ytrue,proba), TP=tp, FN=fn, FP=fp, TN=tn)
    return r

# ---------------- 2. ORIGINAL (flawed) pipeline ----------------
orig = df.copy()
orig["income"] = orig["income"].fillna(orig["income"].mean())                    # D1 global mean
orig = orig.drop(columns="occupation")                                           # D2 drop 18% attribute
orig["income_bin"] = pd.cut(orig["income"], 5, labels=False)                     # D3 equal-width 5 bins
Xo = orig[["age","income_bin","debt_ratio","late_payments","loan_amount"]].astype(float)
Xo = pd.DataFrame(MinMaxScaler().fit_transform(Xo), columns=Xo.columns)          # D4 scaling on full data (leakage)
yo = orig["default"].values
Xo_tr, Xo_te, yo_tr, yo_te = train_test_split(Xo, yo, test_size=0.3, random_state=SEED)   # plain random split
sub = rng.choice(len(Xo_tr), size=int(0.10*len(Xo_tr)), replace=False)          # D5 10% random sample
Xo_tr, yo_tr = Xo_tr.iloc[sub], yo_tr[sub]

# ---------------- 3. REDESIGNED pipeline ----------------
red = df.copy()
red["income_missing"] = red["income"].isna().astype(int)
red["occupation"] = red["occupation"].fillna("Unknown")                          # keep attribute, 'Unknown' category
X = red.drop(columns="default"); yy = red["default"].values
Xtr, Xte, ytr, yte = train_test_split(X, yy, test_size=0.3, stratify=yy, random_state=SEED)  # split FIRST, stratified
# For a fair comparison we evaluate BOTH pipelines on the SAME test rows: the stratified test set.
Xo_full = orig[["age","income_bin","debt_ratio","late_payments","loan_amount"]].astype(float)
tr_all, te_all = Xtr.index, Xte.index
pre = ColumnTransformer([
    ("inc", Pipeline([("imp", SimpleImputer(strategy="median")), ("log", __import__("sklearn.preprocessing",fromlist=["FunctionTransformer"]).FunctionTransformer(np.log1p)),
                      ("bin", KBinsDiscretizer(n_bins=5, encode="onehot-dense", strategy="quantile"))]), ["income"]),
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), ["age","debt_ratio","late_payments","loan_amount"]),
    ("flag", "passthrough", ["income_missing"]),
    ("occ", OneHotEncoder(handle_unknown="ignore"), ["occupation"]),
])
clf = Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=2000, class_weight="balanced"))])
# threshold selected on TRAINING data only (5-fold CV): smallest-FP threshold that keeps recall >= 0.70
cvp = cross_val_predict(clf, Xtr, ytr, cv=StratifiedKFold(5, shuffle=True, random_state=SEED), method="predict_proba")[:,1]
cands = np.linspace(0.05, 0.95, 91)
ok = [t for t in cands if recall_score(ytr, cvp>=t) >= 0.70]
thr = max(ok) if ok else 0.5
clf.fit(Xtr, ytr); p_red = clf.predict_proba(Xte)[:,1]
res_red = report(f"Redesigned (thr={thr:.2f})", yte, (p_red>=thr).astype(int), p_red)
print(f"\nREDESIGNED: training rows={len(ytr)} defaulters in training={ytr.sum()}  CV-selected threshold={thr:.2f}")

# Original pipeline evaluated on the SAME stratified test rows (fair comparison; leakage defect kept for fidelity)
Xo_same_te = Xo.loc[te_all]; Xo_same_tr = Xo.loc[tr_all]
sub2 = np.random.default_rng(SEED).choice(len(Xo_same_tr), size=int(0.10*len(Xo_same_tr)), replace=False)
m0b = LogisticRegression(max_iter=1000).fit(Xo_same_tr.iloc[sub2], ytr[sub2])
res_orig2 = report("Original (flawed)", yte, m0b.predict(Xo_same_te), m0b.predict_proba(Xo_same_te)[:,1])
# default-class baseline: always predict 'no default'
res_base = report("Baseline: predict all 'No default'", yte, np.zeros_like(yte), np.zeros(len(yte))+1e-9)
tab = pd.DataFrame([res_base, res_orig2, res_red]).set_index("Pipeline")
pd.set_option("display.width", 200); pd.set_option("display.float_format", lambda v: f"{v:.4f}")
print("\n=== SAME TEST SET (n=%d, defaulters=%d) ==="%(len(yte), yte.sum())); print(tab.to_string())
tab.to_csv("../out/q7_results.csv")

# ---------------- 4. effect on dispersion & class distribution ----------------
inc_raw = df["income"].dropna()
inc_mean_imp = df["income"].fillna(df["income"].mean())
inc_med_imp = df["income"].fillna(df["income"].median())
def disp(s): return f"SD={s.std():12.1f}  CV={s.std()/s.mean():.3f}  skew={skew(s):.3f}"
print("\nINCOME DISPERSION")
print(" observed only        :", disp(inc_raw))
print(" global-mean imputed  :", disp(inc_mean_imp))
print(" median imputed       :", disp(inc_med_imp))
print(" log(median imputed)  :", disp(np.log(inc_med_imp)))
ys=ytr[sub2]
print(f"\nTRAINING CLASS DISTRIBUTION  original: {ys.sum()}/{len(ys)} = {ys.mean():.2%} defaulters (rows used={len(ys)})")
print(f"                             redesigned (class_weight balanced): effective defaulter weight = 50% ; raw {ytr.mean():.2%} of {len(ytr)} rows")

# ---------------- 5. figures ----------------
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
metrics = ["Accuracy","Precision","Recall","F1"]
xs = np.arange(len(metrics)); w = .38
ax[0].bar(xs-w/2, tab.loc[res_orig2["Pipeline"], metrics], w, label="Original", color="#d95f02")
ax[0].bar(xs+w/2, tab.iloc[2][metrics], w, label="Redesigned", color="#1b9e77")
ax[0].set_xticks(xs); ax[0].set_xticklabels(metrics); ax[0].set_ylim(0,1.05); ax[0].legend(); ax[0].set_title("Test-set metrics (same rows)")
for i,v in enumerate(tab.loc[res_orig2["Pipeline"], metrics]): ax[0].text(i-w/2, v+.01, f"{v:.2f}", ha="center", fontsize=8)
for i,v in enumerate(tab.iloc[2][metrics]): ax[0].text(i+w/2, v+.01, f"{v:.2f}", ha="center", fontsize=8)
ax[1].hist(inc_raw/1000, bins=60, color="#6baed6"); ax[1].set_title("Income distribution (right-skewed)"); ax[1].set_xlabel("Income (thousand)"); ax[1].set_xlim(0,300)
plt.tight_layout(); plt.savefig("../out/q7_comparison.png", dpi=200)

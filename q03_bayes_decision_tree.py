"""Day 3 - Q3: Naive Bayes and Decision-tree classification (buys_computer) using training and test data."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, LeaveOneOut, cross_val_score
from sklearn.naive_bayes import CategoricalNB
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.preprocessing import OrdinalEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

rows = """<=30,high,no,fair,no
<=30,high,no,excellent,no
31...40,high,no,fair,yes
>40,medium,no,fair,yes
>40,low,yes,fair,yes
>40,low,yes,excellent,no
31...40,low,yes,excellent,yes
<=30,medium,no,fair,no
<=30,low,yes,fair,yes
>40,medium,yes,fair,yes
<=30,medium,yes,excellent,yes
31...40,medium,no,excellent,yes
31...40,high,yes,fair,yes
>40,medium,no,excellent,no""".split("\n")
df = pd.DataFrame([r.split(",") for r in rows], columns=["age", "income", "student", "credit_rating", "buys_computer"])
df.index += 1
print(df, "\n")
X, y = df.drop(columns="buys_computer"), df["buys_computer"]

# ---- Part 1: manual Naive Bayes (textbook method) for the unseen tuple ---------------------------------------
new = {"age": "<=30", "income": "medium", "student": "yes", "credit_rating": "fair"}
print("=== NAIVE BAYES by hand for X =", new, "===")
post = {}
for c in ["yes", "no"]:
    sub = df[df.buys_computer == c]; p = len(sub) / len(df); line = f"P({c}) = {len(sub)}/{len(df)} = {p:.3f}"
    for a, v in new.items():
        pa = (sub[a] == v).sum() / len(sub); p *= pa; line += f"\n   P({a}={v} | {c}) = {(sub[a]==v).sum()}/{len(sub)} = {pa:.3f}"
    post[c] = p; print(line, f"\n   P(X | {c}) * P({c}) = {p:.4f}")
print("Prediction: buys_computer =", max(post, key=post.get), " (normalised P(yes|X) = %.3f)\n" % (post["yes"] / sum(post.values())))

# ---- Part 2: train / test split (10 training tuples, 4 test tuples) ----------------------------------------
enc = OrdinalEncoder().fit(X); Xo = enc.transform(X).astype(int); Xh = pd.get_dummies(X).astype(int)   # one-hot for the tree
idx_tr, idx_te = train_test_split(np.arange(len(df)), test_size=4, random_state=1, stratify=y)
print(f"=== TRAIN / TEST SPLIT: {len(idx_tr)} training tuples (RIDs {[int(i) + 1 for i in sorted(idx_tr)]}), {len(idx_te)} test tuples (RIDs {[int(i) + 1 for i in sorted(idx_te)]}) ===")
models = {"Naive Bayes (Laplace smoothing)": (CategoricalNB(alpha=1.0), Xo),
          "Decision Tree (entropy)": (DecisionTreeClassifier(criterion="entropy", random_state=0), Xh)}
for name, (m, XX) in models.items():
    m.fit(XX[idx_tr], y.iloc[idx_tr]) if isinstance(XX, np.ndarray) else m.fit(XX.iloc[idx_tr], y.iloc[idx_tr])
    p = m.predict(XX[idx_te]) if isinstance(XX, np.ndarray) else m.predict(XX.iloc[idx_te])
    print(f"\n{name}: test accuracy = {accuracy_score(y.iloc[idx_te], p):.2%}")
    print("Confusion matrix (rows = actual no/yes, cols = predicted no/yes):\n", confusion_matrix(y.iloc[idx_te], p, labels=["no", "yes"]))
print("\n(Only 4 test tuples - one mistake moves accuracy by 25 points, so leave-one-out CV is also reported.)")
for name, (m, XX) in models.items():
    print(f"Leave-one-out accuracy, {name}: {cross_val_score(m, XX, y, cv=LeaveOneOut()).mean():.2%}")

# ---- Part 3: decision tree on all 14 tuples ---------------------------------------------------------------
dt = DecisionTreeClassifier(criterion="entropy", random_state=0).fit(Xh, y)
print("\nDecision tree rules (trained on all 14 tuples):\n", export_text(dt, feature_names=list(Xh.columns)))
print("Decision-tree prediction for X:", dt.predict(Xh.iloc[[0]].mul(0).add(pd.get_dummies(pd.DataFrame([new])).reindex(columns=Xh.columns, fill_value=0).astype(int).values))[0])
plt.figure(figsize=(14, 8)); plot_tree(dt, feature_names=list(Xh.columns), class_names=list(dt.classes_), filled=True, fontsize=8)
plt.savefig("day3/output/q03_decision_tree.png", dpi=110, bbox_inches="tight")

"""Day 3 - Q8: Rule-based classification (RIPPER, WEKA's JRip) vs decision-tree classification, compare accuracy and plot.
Dataset: diabetes.csv"""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wittgenstein as lw
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

d = pd.read_csv("data/diabetes.csv")
train, test = train_test_split(d, test_size=0.3, random_state=42, stratify=d.Outcome)

rip = lw.RIPPER(random_state=42); rip.fit(train, class_feat="Outcome", pos_class=1)
print("RIPPER rules learned (rule-based classifier):"); print(rip.ruleset_)
pr = np.array(rip.predict(test.drop(columns="Outcome"))).astype(int)

dt = DecisionTreeClassifier(max_depth=4, min_samples_leaf=10, random_state=0).fit(train.drop(columns="Outcome"), train.Outcome)
pd_ = dt.predict(test.drop(columns="Outcome"))
y = test.Outcome.values
res = pd.DataFrame({m: [accuracy_score(y, p), precision_score(y, p), recall_score(y, p), f1_score(y, p)]
                    for m, p in [("Rule-based (RIPPER)", pr), ("Decision tree", pd_)]},
                   index=["Accuracy", "Precision", "Recall", "F1"]).round(4)
print("\nComparison on the 30% test set:\n", res)
ax = res.T.plot.bar(figsize=(8, 5), rot=0, color=["#4c72b0", "#55a868", "#c44e52", "#8172b2"], ylim=(0, 1))
ax.set_title("Rule-based vs Decision-tree classification"); plt.tight_layout(); plt.savefig("day3/output/q08_comparison.png", dpi=120)
print("\nPlot saved: day3/output/q08_comparison.png")

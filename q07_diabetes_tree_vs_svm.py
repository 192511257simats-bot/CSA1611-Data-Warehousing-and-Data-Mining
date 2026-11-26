"""Day 4 Exercise - Q7: Diabetes prediction: Decision tree (J48) vs SVM (SMO); accuracy and F1 calculated by hand from the confusion matrix."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix

d = pd.read_csv("data/diabetes.csv"); X, y = d.drop(columns="Outcome"), d.Outcome
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
models = {"Decision Tree (J48-like)": DecisionTreeClassifier(max_depth=4, min_samples_leaf=10, random_state=0),
          "SVM (RBF, like SMO)": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1.0))}
res = {}
for name, m in models.items():
    p = m.fit(Xtr, ytr).predict(Xte); tn, fp, fn, tp = confusion_matrix(yte, p).ravel()
    acc = (tp + tn) / (tp + tn + fp + fn); pre = tp / (tp + fp); rec = tp / (tp + fn); f1 = 2 * pre * rec / (pre + rec)
    res[name] = dict(Accuracy=acc, Precision=pre, Recall=rec, F1=f1)
    print(f"=== {name} ===\nConfusion matrix: TN={tn} FP={fp} FN={fn} TP={tp}")
    print(f"Accuracy  = (TP+TN)/(TP+TN+FP+FN) = ({tp}+{tn})/{tp+tn+fp+fn} = {acc:.4f}")
    print(f"Precision = TP/(TP+FP) = {tp}/{tp+fp} = {pre:.4f}\nRecall    = TP/(TP+FN) = {tp}/{tp+fn} = {rec:.4f}")
    print(f"F1        = 2*P*R/(P+R) = {f1:.4f}\n")
r = pd.DataFrame(res).round(4); print("SUMMARY\n", r.to_string())
ax = r.T.plot.bar(figsize=(8, 5), rot=0, ylim=(0, 1)); ax.set_title("Diabetes prediction: Decision tree vs SVM"); plt.tight_layout(); plt.savefig("day4/exercises/output/q07_tree_vs_svm.png", dpi=120)
w = r.loc["F1"].idxmax()
print(f"\nExplanation: {w} has the better F1 on the positive (diabetic) class. Recall is the lower metric for both models because the data is imbalanced (65% negative),\nso many diabetic patients are missed - in a medical setting recall (sensitivity) deserves extra weight.")

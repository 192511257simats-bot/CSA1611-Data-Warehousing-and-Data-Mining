"""Day 4 Exercise - Q3: Naive Bayes vs SVM (WEKA NaiveBayes vs SMO) on the Wisconsin breast-cancer dataset; summary + graph."""
import pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, cohen_kappa_score, confusion_matrix

d = load_breast_cancer(); X, y = d.data, d.target
print(f"Dataset: breast cancer, {X.shape[0]} instances, {X.shape[1]} numeric attributes, classes = {list(d.target_names)}\nEvaluation: stratified 10-fold cross-validation\n")
models = {"Naive Bayes": GaussianNB(), "SVM (linear kernel, like WEKA SMO)": make_pipeline(StandardScaler(), SVC(kernel="linear", C=1.0))}
cv = StratifiedKFold(10, shuffle=True, random_state=1); res = {}
for name, m in models.items():
    p = cross_val_predict(m, X, y, cv=cv)
    res[name] = dict(Accuracy=accuracy_score(y, p), Precision=precision_score(y, p), Recall=recall_score(y, p), F1=f1_score(y, p), Kappa=cohen_kappa_score(y, p))
    print(f"=== {name} ===\nCorrectly classified: {(p == y).sum()} ({accuracy_score(y, p):.2%})  Incorrectly: {(p != y).sum()}")
    print("Confusion matrix (malignant, benign):\n", confusion_matrix(y, p))
r = pd.DataFrame(res).round(4); print("\nSUMMARY OF RESULTS\n", r.to_string())
ax = r.drop(index="Kappa").plot.bar(figsize=(8, 5), rot=0, ylim=(0.85, 1.0)); ax.set_title("Naive Bayes vs SVM (10-fold CV)"); ax.set_ylabel("score")
plt.tight_layout(); plt.savefig("day4/exercises/output/q03_nb_vs_svm.png", dpi=120)
best = r.loc["Accuracy"].idxmax(); print(f"\nConclusion: {best} gives the higher accuracy. SVM handles correlated features better; Naive Bayes assumes independent features but is faster.")

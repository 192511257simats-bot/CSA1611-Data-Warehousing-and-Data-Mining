"""Day 3 - Q6: Categorical prediction with a decision tree + preprocessing + logistic regression
(WEKA's  a) Tree = J48,  b) Preprocess = filters,  c) Logistic = Logistic classifier).  Dataset: diabetes.csv"""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

d = pd.read_csv("data/diabetes.csv")
print("=== b) PREPROCESS ===")
print("Shape:", d.shape, "| class distribution:\n", d.Outcome.value_counts().to_string())
zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
print("\nMissing values coded as 0 :", (d[zero_cols] == 0).sum().to_dict())
d[zero_cols] = d[zero_cols].replace(0, np.nan)
d[zero_cols] = d[zero_cols].fillna(d[zero_cols].median())                 # ReplaceMissingValues filter
X, y = d.drop(columns="Outcome"), d.Outcome
Xn = pd.DataFrame(MinMaxScaler().fit_transform(X), columns=X.columns)      # Normalize filter
print("After median imputation and min-max normalisation (first 3 rows):\n", Xn.head(3).round(3).to_string())

Xtr, Xte, ytr, yte = train_test_split(Xn, y, test_size=0.33, random_state=42, stratify=y)
tree = DecisionTreeClassifier(max_depth=4, min_samples_leaf=10, random_state=0).fit(Xtr, ytr)
logit = LogisticRegression(max_iter=1000).fit(Xtr, ytr)

for name, m in [("a) TREE (J48-style decision tree)", tree), ("c) LOGISTIC regression", logit)]:
    p = m.predict(Xte)
    print(f"\n=== {name} ===\nTest accuracy = {accuracy_score(yte, p):.2%}   10-fold CV accuracy = {cross_val_score(m, Xn, y, cv=10).mean():.2%}")
    print("Confusion matrix:\n", confusion_matrix(yte, p))
    print(classification_report(yte, p, target_names=["tested_negative", "tested_positive"]))
print("Decision tree (text):\n", export_text(tree, feature_names=list(X.columns)))
print("Logistic regression coefficients (normalised inputs):\n", pd.Series(logit.coef_[0], X.columns).round(2).sort_values().to_string())
plt.figure(figsize=(16, 8)); plot_tree(tree, feature_names=list(X.columns), class_names=["neg", "pos"], filled=True, fontsize=8)
plt.savefig("day3/output/q06_tree.png", dpi=110, bbox_inches="tight")

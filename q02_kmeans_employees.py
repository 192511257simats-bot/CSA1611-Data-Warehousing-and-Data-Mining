"""Day 4 Exercise - Q2: Employee CSV dataset -> K-Means (WEKA SimpleKMeans equivalent) with different cluster sizes + plots."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

df = pd.DataFrame({"EmployeID": [111, 222, 333, 444, 555, 666], "Gender": ["Male", "Male", "Female", "Female", "Female", "Male"],
                   "Age": [28, 25, 26, 25, 30, 29], "Salary": [150000, 150000, 160000, 160000, 170000, 200000], "Credit": [39, 27, 42, 40, 64, 72]})
df.to_csv("day4/exercises/output/q02_employees.csv", index=False)
with open("day4/exercises/output/q02_employees.arff", "w") as f:
    f.write("@relation employees\n@attribute EmployeID numeric\n@attribute Gender {Male,Female}\n@attribute Age numeric\n@attribute Salary numeric\n@attribute Credit numeric\n@data\n")
    for r in df.itertuples(index=False): f.write(",".join(map(str, r)) + "\n")
print(df.to_string(index=False), "\n\nFiles: q02_employees.csv and q02_employees.arff (open either in WEKA Preprocess tab).")
X = df[["Age", "Salary", "Credit"]].copy(); X["Male"] = (df.Gender == "Male").astype(int)
Xs = MinMaxScaler().fit_transform(X)                       # WEKA's SimpleKMeans also normalises numeric attributes
fig, axs = plt.subplots(1, 3, figsize=(16, 4.6)); sse = {}
for ax, k in zip(axs, [2, 3, 4]):
    km = KMeans(k, n_init=20, random_state=1).fit(Xs); sse[k] = km.inertia_
    print(f"\n=== k = {k} === within-cluster SSE = {km.inertia_:.4f}")
    for c in range(k):
        m = df[km.labels_ == c]; print(f"  Cluster {c}: employees {m.EmployeID.tolist()}  mean age {m.Age.mean():.1f}, salary {m.Salary.mean():,.0f}, credit {m.Credit.mean():.1f}")
    ax.scatter(df.Salary, df.Credit, c=km.labels_, cmap="Set1", s=120, edgecolor="k")
    for r in df.itertuples(): ax.annotate(str(r.EmployeID), (r.Salary, r.Credit), textcoords="offset points", xytext=(6, 6))
    ax.set_title(f"K-Means, k = {k}"); ax.set_xlabel("Salary"); ax.set_ylabel("Credit")
plt.tight_layout(); plt.savefig("day4/exercises/output/q02_clusters_k2_k3_k4.png", dpi=120)
plt.figure(figsize=(5, 4)); plt.plot(list(sse), list(sse.values()), "bo-"); plt.xlabel("k"); plt.ylabel("SSE"); plt.title("SSE vs cluster size")
plt.tight_layout(); plt.savefig("day4/exercises/output/q02_sse.png", dpi=120)
print("\nSSE falls as k grows (k = 6 would give 0); k = 2 or 3 gives meaningful groups: a high salary / high credit group (555, 666) vs the rest.")

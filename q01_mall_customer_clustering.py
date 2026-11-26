"""Day 4 Exercise - Q1: Mall customer segmentation with K-Means (Annual Income vs Spending Score).
NOTE: the first 5 rows are the sample rows from the question; the remaining 195 rows are SYNTHETIC (seeded random numbers
drawn around five income/spending groups) because the original mall dataset was not supplied."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

rng = np.random.default_rng(42)
# (income k$, spending score, age mean, age sd, n)  -> five natural groups
groups = [(55, 50, 42, 12, 45), (26, 20, 40, 12, 30), (26, 79, 25, 5, 30), (87, 18, 45, 8, 35), (87, 82, 32, 5, 55)]
rows = []
for inc, sp, am, asd, n in groups:
    for _ in range(n):
        rows.append((rng.normal(inc, 7), np.clip(rng.normal(sp, 8), 1, 99), np.clip(rng.normal(am, asd), 18, 70)))
rng.shuffle(rows)
df = pd.DataFrame(rows[:195], columns=["Annual Income (k$)", "Spending Score (1-100)", "Age"]).round(0).astype(int)
df["Gender"] = rng.choice(["Male", "Female"], len(df))
sample = pd.DataFrame({"Gender": ["Male", "Male", "Female", "Female", "Female"], "Age": [19, 21, 20, 23, 31],
                       "Annual Income (k$)": [15, 15, 16, 16, 17], "Spending Score (1-100)": [39, 81, 6, 77, 40]})
df = pd.concat([sample, df], ignore_index=True); df.insert(0, "CustomerID", range(1, len(df) + 1))
df = df[["CustomerID", "Gender", "Age", "Annual Income (k$)", "Spending Score (1-100)"]]
df.to_csv("day4/exercises/output/q01_mall_customers.csv", index=False)
print("Dataset created: day4/exercises/output/q01_mall_customers.csv", df.shape); print(df.head().to_string(index=False))

X = df[["Annual Income (k$)", "Spending Score (1-100)"]]
print("\nElbow method / silhouette score for k = 2..10")
wcss, sil = [], []
for k in range(2, 11):
    km = KMeans(k, n_init=10, random_state=42).fit(X); wcss.append(km.inertia_); sil.append(silhouette_score(X, km.labels_))
    print(f"  k={k:2d}  WCSS={km.inertia_:10.1f}  silhouette={sil[-1]:.3f}")
km = KMeans(5, n_init=10, random_state=42).fit(X); df["Cluster"] = km.labels_
cent = pd.DataFrame(km.cluster_centers_, columns=["income", "spending"]).round(1)
cent["age"] = df.groupby("Cluster").Age.mean().round(1).values; cent["size"] = df.Cluster.value_counts().sort_index().values
def name(r):
    hi_i, hi_s = r.income >= 70, r.spending >= 60
    if hi_i and hi_s: return "Priority Customers"
    if hi_i and not hi_s: return "Senior Citizen Target Customers" if r.age >= 40 else "Careful (high income, low spend)"
    if not hi_i and r.spending >= 60: return "Young Target Customers"
    if r.income < 40 and r.spending < 40: return "Low-priority Customers"
    return "Usual Customers"
cent["segment"] = cent.apply(name, axis=1)
print("\nK-Means with k = 5 - cluster centres:\n", cent.to_string())
df["Segment"] = df.Cluster.map(cent.segment); print("\nCustomers per segment:\n", df.Segment.value_counts().to_string())
df.to_csv("day4/exercises/output/q01_mall_customers_segmented.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(range(2, 11), wcss, "bo-"); ax[0].axvline(5, ls="--", c="r"); ax[0].set_title("Elbow method"); ax[0].set_xlabel("k"); ax[0].set_ylabel("WCSS")
for c in range(5):
    s = df[df.Cluster == c]; ax[1].scatter(s["Annual Income (k$)"], s["Spending Score (1-100)"], s=25, label=cent.segment[c])
ax[1].scatter(cent.income, cent.spending, c="k", marker="X", s=200, label="Centroids")
ax[1].set_xlabel("Annual income (k$)"); ax[1].set_ylabel("Spending score"); ax[1].set_title("Customer segments (k = 5)"); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig("day4/exercises/output/q01_segments.png", dpi=120)
print("\nMarketing insight: Priority + Young Target customers are the ones who convert most easily (high spending score).")

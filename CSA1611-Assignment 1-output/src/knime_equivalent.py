"""knime_equivalent.py - Task 9: exports the CSV files a KNIME workflow reads and reproduces the same node chain in pandas,
so the KNIME report can be cross-checked (CSV Reader -> Joiner -> Row Filter -> GroupBy -> Pivoting -> chart -> report)."""
import sqlite3, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
con = sqlite3.connect("fc_100000.db")
pd.read_sql("SELECT * FROM fact_sales", con).to_csv("out/fact_sales.csv", index=False)
for t in ("dim_date", "dim_product", "dim_store", "dim_customer"): pd.read_sql(f"SELECT * FROM {t}", con).to_csv(f"out/{t}.csv", index=False)
f = pd.read_csv("out/fact_sales.csv"); d = pd.read_csv("out/dim_date.csv"); p = pd.read_csv("out/dim_product.csv"); s = pd.read_csv("out/dim_store.csv")
print("CSV Reader   : fact rows =", len(f))
j = f.merge(d, on="date_key").merge(p, on="product_key").merge(s, on="store_key")        # Joiner nodes
print("Joiner       : joined rows =", len(j), "(must equal fact rows)")
r = j[(j.quantity > 0) & (j.year.isin([2025, 2026]))]                                   # Row Filter
print("Row Filter   : rows kept =", len(r))
g = r.groupby(["region", "year_quarter"], as_index=False).net_amount.sum()               # GroupBy
pv = g.pivot(index="region", columns="year_quarter", values="net_amount").round(0)       # Pivoting
print("Pivoting     : net sales (INR) by region x quarter"); print(pv.to_string())
print("Reconciliation: pivot grand total =", f"{pv.sum().sum():,.2f}", "| SUM(fact net_amount) =", f"{f.net_amount.sum():,.2f}")
fig, ax = plt.subplots(figsize=(9, 3.6)); (pv.T / 1e6).plot(kind="bar", ax=ax); ax.set_ylabel("Net sales (INR million)"); ax.set_title("FreshCart - net sales by region and quarter (100,000 fact rows)")
plt.xticks(rotation=0); plt.tight_layout(); fig.savefig("img/fig_knime_report.png", dpi=150)

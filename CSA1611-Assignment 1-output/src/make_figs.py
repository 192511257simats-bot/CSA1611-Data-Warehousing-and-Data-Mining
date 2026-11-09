import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
C = dict(src="#FCE4D6", stg="#FFF2CC", etl="#E2EFDA", dw="#DDEBF7", mart="#D9D2E9", fe="#F8CBAD", meta="#EDEDED", fact="#BDD7EE", dim="#E2EFDA", new="#FFD966")
def box(ax, x, y, w, h, t, c="#DDEBF7", fs=8, bold=False, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=c, ec="#333", lw=1, ls=ls))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", wrap=True)
def arrow(ax, a, b, ls="-", txt=None):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12, lw=1.2, color="#333", ls=ls))
    if txt: ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + .12, txt, fontsize=7, ha="center")
def fig(w, h, title):
    f, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); ax.set_title(title, fontsize=11, fontweight="bold"); return f, ax

# ---- Fig 1 architecture
f, ax = fig(12, 6.4, "Figure 2.1  FreshCart enterprise data warehouse architecture (dependent data marts, ROLAP/HOLAP server)")
box(ax, .2, 4.2, 1.9, 1.3, "OLTP DB\n(Orders, OrderLines,\nCustomers, Products,\nStores, Promotions,\nReturns)", C["src"])
box(ax, .2, 2.6, 1.9, 1.1, "Loyalty-card &\nPromotion systems\n(CSV / API)", C["src"])
box(ax, .2, 1.0, 1.9, 1.1, "Online channel\n(Day-4 source,\n20,000 orders/day)", C["src"], ls="--")
box(ax, 2.7, 2.3, 1.6, 2.2, "STAGING AREA\nraw copies,\nno business rules\nrejects + audit\ntables", C["stg"])
box(ax, 4.9, 2.3, 1.7, 2.2, "ETL\nextract - clean -\nconform - SCD -\nsurrogate-key\nlookup - load", C["etl"], bold=True)
box(ax, 7.2, 3.9, 2.0, 1.6, "ENTERPRISE DATA\nWAREHOUSE\nstar schemas:\nfact_sales, fact_returns\n+ conformed dims", C["dw"], bold=True)
box(ax, 7.2, 1.9, 2.0, 1.5, "Aggregates /\nmaterialised cuboids\n(agg_sales)", C["dw"])
box(ax, 7.2, 0.2, 2.0, 1.2, "METADATA REPOSITORY\nschema, lineage, ETL\nrules, refresh log", C["meta"])
box(ax, 9.8, 3.9, 2.0, 1.1, "Dependent data marts\nSales | Merchandising |\nMarketing/Loyalty", C["mart"])
box(ax, 9.8, 2.3, 2.0, 1.1, "OLAP SERVER\n(ROLAP/HOLAP):\nroll-up, drill, slice,\ndice, pivot", C["mart"], bold=True)
box(ax, 9.8, .2, 2.0, 1.7, "FRONT-END TOOLS\nreports - ad-hoc query -\ndashboards (Superset) -\nKNIME workflows -\nPython OLAP app", C["fe"])
for a, b in [((2.1, 4.8), (2.7, 3.9)), ((2.1, 3.1), (2.7, 3.4)), ((2.1, 1.6), (2.7, 2.7)), ((4.3, 3.4), (4.9, 3.4)), ((6.6, 3.8), (7.2, 4.5)),
             ((8.2, 3.9), (8.2, 3.4)), ((9.2, 4.5), (9.8, 4.5)), ((9.2, 2.7), (9.8, 2.85)), ((10.8, 2.3), (10.8, 1.9)), ((8.2, 1.9), (8.2, 1.4)), ((9.2, 2.6), (9.8, 2.6))]:
    arrow(ax, a, b)
arrow(ax, (10.8, 3.9), (10.8, 3.4)); arrow(ax, (5.75, 2.3), (7.2, 1.0), "--", "metadata"); ax.text(.2, .3, "dashed = added in Day-4 redesign / metadata flow", fontsize=7)
f.savefig("img/fig_arch.png", dpi=150, bbox_inches="tight"); plt.close(f)

# ---- Fig 2 star schema
def table(ax, x, y, w, title, cols, c):
    h = .32 * (len(cols) + 1.3)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.05", fc=c, ec="#333", lw=1))
    ax.text(x + w / 2, y + h - .17, title, ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.plot([x, x + w], [y + h - .33, y + h - .33], color="#333", lw=.8)
    for i, t in enumerate(cols): ax.text(x + .08, y + h - .55 - i * .3, t, fontsize=6.8, va="center", family="monospace")
    return (x + w / 2, y + h / 2)
f, ax = fig(13, 10.4, "Figure 3.1  FreshCart star schema (grain: one product line on one order)")
fs = table(ax, 5.0, 2.9, 3.0, "FACT_SALES", ["PK(order_id, line_no)  [degenerate]", "FK date_key", "FK product_key", "FK store_key", "FK customer_key", "FK promo_key",
      "quantity            (additive)", "gross_amount        (additive)", "discount_amount     (additive)", "net_amount          (additive)", "unit_price          (non-additive)"], C["fact"])
table(ax, .2, 7.2, 3.7, "DIM_DATE", ["PK date_key (yyyymmdd)", "full_date, day_of_week, is_weekend", "month_num, month_name", "year_month, quarter_num", "year_quarter, year", "hierarchy: day>month>quarter>year"], C["dim"])
table(ax, 4.6, 7.9, 3.9, "DIM_PRODUCT", ["PK product_key (surrogate)", "product_id (natural), product_name", "brand, category, department, list_price", "hierarchy: product>category>department"], C["dim"])
table(ax, 9.2, 7.2, 3.6, "DIM_STORE", ["PK store_key (surrogate)", "store_id, store_name", "city, state, region", "hierarchy: store>city>state>region"], C["dim"])
table(ax, .2, 3.4, 3.7, "DIM_CUSTOMER", ["PK customer_key (surrogate)", "customer_id, customer_name", "city, state", "segment, loyalty_tier", "SCD Type 1 (original)"], C["dim"])
table(ax, 9.2, 3.4, 3.6, "DIM_PROMOTION", ["PK promo_key (surrogate)", "promo_id, promo_name", "promo_type, discount_pct", "key 0 = 'No Promotion'"], C["dim"])
table(ax, 4.7, .2, 3.6, "FACT_RETURNS (2nd process)", ["FK date_key, product_key", "FK store_key, customer_key", "order_id, line_no (degenerate)", "return_qty, refund_amount (additive)", "reason"], C["fact"])
for p, q in [((3.9, 7.6), (5.0, 6.4)), ((6.5, 7.9), (6.5, 6.8)), ((9.2, 7.6), (8.0, 6.4)), ((3.9, 4.3), (5.0, 4.6)), ((9.2, 4.2), (8.0, 4.6))]: arrow(ax, p, q)
for tgt in [(2.0, 7.2), (4.6, 8.5), (10.2, 7.2), (1.5, 3.4)]: ax.plot([6.5, tgt[0]], [2.4, tgt[1]], "--", color="#999", lw=.8)
ax.text(8.7, .6, "Dashed lines: FACT_RETURNS shares the conformed\ndimensions DATE, PRODUCT, STORE, CUSTOMER\nwith FACT_SALES (drill-across possible).", fontsize=8)
f.savefig("img/fig_star.png", dpi=150, bbox_inches="tight"); plt.close(f)

# ---- Fig 3 snowflake
f, ax = fig(13, 5.6, "Figure 4.1  Snowflaked Product and Store dimensions (extra tables highlighted)")
box(ax, 5.2, 2.3, 2.6, 1.2, "FACT_SALES\n(product_key, store_key, ...)", C["fact"], 9, True)
chain = [("DIM_PRODUCT\n50,000 rows", 0.3, 4.3), ("DIM_BRAND\n800 rows", 2.7, 4.3), ("DIM_CATEGORY\n60 rows", 5.1, 4.3), ("DIM_DEPARTMENT\n12 rows", 7.5, 4.3)]
for i, (t, x, y) in enumerate(chain):
    box(ax, x, y, 2.0, .9, t, C["dim"] if i == 0 else C["new"], 8)
    if i: arrow(ax, (chain[i - 1][1] + 2.0, y + .45), (x, y + .45))
arrow(ax, (5.9, 3.5), (1.3, 4.3), "-", "product_key")
chain2 = [("DIM_STORE\n120 rows", 0.3, .6), ("DIM_CITY\n70 rows", 2.7, .6), ("DIM_STATE\n6 rows", 5.1, .6), ("DIM_REGION\n3 rows", 7.5, .6)]
for i, (t, x, y) in enumerate(chain2):
    box(ax, x, y, 2.0, .9, t, C["dim"] if i == 0 else C["new"], 8)
    if i: arrow(ax, (chain2[i - 1][1] + 2.0, y + .45), (x, y + .45))
arrow(ax, (5.9, 2.3), (1.3, 1.5), "-", "store_key")
ax.text(10.1, 4.6, "Product: +3 tables, +3 joins", fontsize=9); ax.text(10.1, 1.0, "Store: +3 tables, +3 joins", fontsize=9)
f.savefig("img/fig_snowflake.png", dpi=150, bbox_inches="tight"); plt.close(f)

# ---- Fig 4 ETL flow
f, ax = fig(12.5, 5.2, "Figure 5.1  ETL flow for the FreshCart load (dimensions first, then facts)")
steps = [("EXTRACT\nfull (initial) /\nincremental (CDC by\nupdated_at watermark)", C["src"]), ("STAGE\nraw copy + load\nbatch id", C["stg"]), ("CLEAN\ndates, price, case,\nseparators, currency,\nnulls", C["etl"]),
         ("CONFORM\nstore / product /\ncustomer matching;\nSCD logic", C["etl"]), ("DIM LOAD\nthen\nSURROGATE-KEY\nLOOKUP", C["dw"]), ("FACT LOAD\nfact_sales,\nfact_returns", C["dw"]), ("AUDIT\nrow counts,\ncontrol totals,\nrefresh agg", C["meta"])]
for i, (t, c) in enumerate(steps):
    box(ax, .2 + i * 1.75, 2.4, 1.55, 1.7, t, c, 7.5)
    if i: arrow(ax, (.2 + i * 1.75 - .2, 3.25), (.2 + i * 1.75, 3.25))
box(ax, 3.9, .4, 2.8, 1.1, "REJECT / SUSPENSE TABLE\nqty<=0, unparsable date\n(with reason code)", "#F4B6B6", 7.5)
arrow(ax, (4.1, 2.4), (4.9, 1.5)); arrow(ax, (6.2, 2.4), (5.9, 1.5), "--")
box(ax, 8.1, .4, 2.8, 1.1, "UNKNOWN MEMBERS (-1)\nnull store / product ->\nflag, fix later", C["new"], 7.5); arrow(ax, (7.3, 2.4), (9.0, 1.5))
f.savefig("img/fig_etl.png", dpi=150, bbox_inches="tight"); plt.close(f)

# ---- Fig 5 KNIME workflow layout
f, ax = fig(13, 4.6, "Figure 9.1  KNIME workflow layout (node chain for the management report)")
nodes = [("CSV Reader\nfact_sales.csv", C["src"]), ("CSV Reader\ndim_*.csv", C["src"]), ("Joiner\n(fact + dims)", C["etl"]), ("Row Filter\nqty>0, 2025-26", C["etl"]), ("Rule Engine /\nString Manip.\n(clean)", C["etl"]),
         ("GroupBy\nsum(net)", C["dw"]), ("Pivoting\nregion x quarter", C["dw"]), ("Bar Chart\n+ Line Plot", C["fe"]), ("Excel/PDF\nReport Writer", C["fe"])]
xs = [.2, .2, 1.9, 3.6, 5.3, 7.0, 8.7, 10.4, 11.9]; ys = [3.1, 1.3, 2.2, 2.2, 2.2, 2.2, 2.2, 3.1, 1.3]
for (t, c), x, y in zip(nodes, xs, ys): box(ax, x, y, 1.45, 1.0, t, c, 7.5)
for a, b in [(0, 2), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (6, 8)]: arrow(ax, (xs[a] + 1.45, ys[a] + .5), (xs[b], ys[b] + .5))
ax.text(.2, .3, "Extract-clean = ETL (Task 5) | GroupBy / Pivoting = roll-up / pivot (Task 6)", fontsize=8)
f.savefig("img/fig_knime.png", dpi=150, bbox_inches="tight"); plt.close(f)

# ---- Fig 6 revised schema
f, ax = fig(13, 6.6, "Figure 11.1  Revised design: online channel, SCD Type 2 customer, delivery partner, product crosswalk")
box(ax, 5.0, 2.7, 3.0, 2.2, "FACT_SALES (same grain)\n+ channel_key  (NEW)\n+ partner_key  (NEW)\ncustomer_key -> version\nvalid at order time\n+ order_ts (hour)", C["fact"], 8, True)
box(ax, .2, 5.0, 3.2, 1.2, "DIM_CUSTOMER (SCD-2)\ncustomer_key, customer_id, address,\ncity, state, loyalty_tier,\nvalid_from, valid_to, is_current", C["new"], 7.5)
box(ax, 4.8, 5.4, 3.4, 1.0, "DIM_PRODUCT  (unchanged)\n+ PRODUCT_XREF(source_system,\nsource_code -> product_key)  NEW", C["new"], 7.5)
box(ax, 9.6, 5.0, 3.2, 1.2, "DIM_DELIVERY_PARTNER (NEW)\npartner_key, name, type\nkey 0 = 'Not applicable'", C["new"], 7.5)
box(ax, .2, 2.8, 3.2, 1.0, "DIM_CHANNEL (NEW)\n1 In-store | 2 Online", C["new"], 8)
box(ax, 9.6, 2.8, 3.2, 1.0, "DIM_DATE, DIM_STORE,\nDIM_PROMOTION (unchanged)\n+ Online-Hub store row", C["dim"], 8)
box(ax, 4.9, .5, 3.2, 1.2, "AGG_SALES_V2 (+channel)\nincremental UPSERT\nevery hour", C["dw"], 8)
box(ax, .2, .5, 3.4, 1.4, "STAGING (hourly micro-batch)\nonline orders - product codes\nconverted via XREF", C["stg"], 8)
for a, b in [((1.8, 5.0), (5.0, 4.2)), ((6.5, 5.4), (6.5, 4.9)), ((9.6, 5.0), (8.0, 4.2)), ((3.4, 3.3), (5.0, 3.5)), ((9.6, 3.3), (8.0, 3.5)), ((6.5, 2.7), (6.5, 1.7)), ((3.6, 1.2), (4.9, 1.1))]: arrow(ax, a, b)
f.savefig("img/fig_revised.png", dpi=150, bbox_inches="tight"); plt.close(f)

# ---- Fig 7 performance charts
sizes = [1000, 10000, 100000, 1000000]; R = {s: json.load(open(f"fc_{s}_bench.json")) for s in sizes}
f, axs = plt.subplots(1, 3, figsize=(13, 3.8)); cfg = [("oltp", "(i) OLTP schema"), ("star", "(ii) star"), ("star_idx", "(iii-a) star + indexes"), ("agg", "(iii-b) star + summary")]
for ax, qk in zip(axs, R[1000]["queries"]):
    for k, lab in cfg: ax.plot(sizes, [R[s]["queries"][qk][k]["time_s"] * 1000 for s in sizes], marker="o", label=lab)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(qk.split(" ")[0] + " " + " ".join(qk.split(" ")[1:5]) + "...", fontsize=9); ax.set_xlabel("fact rows"); ax.set_ylabel("time (ms)"); ax.grid(alpha=.3)
axs[0].legend(fontsize=7); f.suptitle("Figure 8.1  Query execution time vs data size (median of 3 runs, log-log)", fontsize=10)
f.savefig("img/fig_perf.png", dpi=150, bbox_inches="tight"); plt.close(f)
f, ax = plt.subplots(figsize=(7, 3.4)); import numpy as np
q = list(R[1000000]["queries"]); w = .2
for i, (k, lab) in enumerate(cfg): ax.bar(np.arange(3) + i * w, [R[1000000]["queries"][x][k]["vm_steps_k"] for x in q], w, label=lab)
ax.set_xticks(np.arange(3) + 1.5 * w); ax.set_xticklabels(["Q1", "Q2", "Q3"]); ax.set_yscale("log"); ax.set_ylabel("SQLite VM steps (thousands)"); ax.legend(fontsize=7); ax.set_title("Figure 8.2  Work done at 1,000,000 fact rows", fontsize=9)
f.savefig("img/fig_work.png", dpi=150, bbox_inches="tight"); plt.close(f)
print("figs done")

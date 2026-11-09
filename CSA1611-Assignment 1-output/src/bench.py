"""bench.py - Task 8: run 3 analytical queries on (i) OLTP schema, (ii) star schema, (iii) star + indexes + summary table.
Usage: python bench.py <db_path>     Writes <db>_bench.json
Metrics: median time of 3 runs, SQLite VM steps (work proxy), rows scanned by full table scans (from the query plan),
joins, plan text, and storage / build time of the extra structures."""
import sqlite3, sys, time, json, os, re, statistics

Q = {
 "Q1 net sales by region, category, quarter": {
  "oltp": """SELECT r.region_name, c.category_name,
      strftime('%Y',o.order_date)||'-Q'||((CAST(strftime('%m',o.order_date) AS INT)+2)/3) AS q, SUM(l.qty*l.unit_price-l.discount)
      FROM order_lines l JOIN orders o ON o.order_id=l.order_id JOIN products p ON p.product_id=l.product_id
      JOIN brands b ON b.brand_id=p.brand_id JOIN categories c ON c.category_id=b.category_id
      JOIN stores s ON s.store_id=o.store_id JOIN cities ci ON ci.city_id=s.city_id
      JOIN states st ON st.state_id=ci.state_id JOIN regions r ON r.region_id=st.region_id GROUP BY 1,2,3""",
  "star": """SELECT s.region, p.category, d.year_quarter, SUM(f.net_amount) FROM fact_sales f
      JOIN dim_date d ON d.date_key=f.date_key JOIN dim_product p ON p.product_key=f.product_key
      JOIN dim_store s ON s.store_key=f.store_key GROUP BY 1,2,3""",
  "agg": "SELECT region, category, year_quarter, SUM(net_sales) FROM agg_sales GROUP BY 1,2,3"},
 "Q2 weekend vs weekday net sales by department": {
  "oltp": """SELECT dp.department_name, CASE WHEN strftime('%w',o.order_date) IN ('0','6') THEN 'Weekend' ELSE 'Weekday' END, SUM(l.qty*l.unit_price-l.discount)
      FROM order_lines l JOIN orders o ON o.order_id=l.order_id JOIN products p ON p.product_id=l.product_id
      JOIN brands b ON b.brand_id=p.brand_id JOIN categories c ON c.category_id=b.category_id
      JOIN departments dp ON dp.department_id=c.department_id GROUP BY 1,2""",
  "star": """SELECT p.department, CASE d.is_weekend WHEN 1 THEN 'Weekend' ELSE 'Weekday' END, SUM(f.net_amount) FROM fact_sales f
      JOIN dim_date d ON d.date_key=f.date_key JOIN dim_product p ON p.product_key=f.product_key GROUP BY 1,2""",
  "agg": "SELECT department, CASE is_weekend WHEN 1 THEN 'Weekend' ELSE 'Weekday' END, SUM(net_sales) FROM agg_sales GROUP BY 1,2"},
 "Q3 YTD (Jan-Oct) net sales by state, 2026 vs 2025": {
  "oltp": """SELECT st.state_name, strftime('%Y',o.order_date), SUM(l.qty*l.unit_price-l.discount)
      FROM order_lines l JOIN orders o ON o.order_id=l.order_id JOIN stores s ON s.store_id=o.store_id
      JOIN cities ci ON ci.city_id=s.city_id JOIN states st ON st.state_id=ci.state_id
      WHERE CAST(strftime('%m',o.order_date) AS INT)<=10 GROUP BY 1,2""",
  "star": """SELECT s.state, d.year, SUM(f.net_amount) FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
      JOIN dim_store s ON s.store_key=f.store_key WHERE d.month_num<=10 GROUP BY 1,2""",
  "agg": "SELECT state, year, SUM(net_sales) FROM agg_sales WHERE month_num<=10 GROUP BY 1,2"}}
JOINS = {"Q1": (8, 3, 0), "Q2": (5, 2, 0), "Q3": (4, 2, 0)}


def run(con, sql):
    steps = [0]
    con.set_progress_handler(lambda: steps.__setitem__(0, steps[0] + 1) or 0, 1000)
    ts = []
    for _ in range(3):
        steps[0] = 0; t = time.perf_counter(); rows = con.execute(sql).fetchall(); ts.append(time.perf_counter() - t)
    con.set_progress_handler(None, 0)
    plan = [r[3] for r in con.execute("EXPLAIN QUERY PLAN " + sql)]
    return dict(time_s=round(statistics.median(ts), 4), vm_steps_k=steps[0], rows=len(rows), plan=plan,
                total=round(sum(r[-1] for r in rows), 2))


def scanned(con, plan, sql):
    """rows touched by FULL scans: sum of table cardinalities for 'SCAN <table|alias>' lines."""
    alias = {a: t for t, a in re.findall(r"(?:FROM|JOIN)\s+(\w+)\s+(?:AS\s+)?(\w+)\b", sql)}
    tot = 0
    for p in plan:
        m = re.match(r"SCAN (\w+)", p)
        if m:
            t = alias.get(m.group(1), m.group(1))
            try: tot += con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except sqlite3.Error: pass
    return tot


def main(path):
    con = sqlite3.connect(path); res = {"queries": {}}
    cards = {}
    for key, qd in Q.items():
        res["queries"][key] = {}
        for cfg in ("oltp", "star"):
            r = run(con, qd[cfg]); r["rows_scanned"] = scanned(con, r["plan"], qd[cfg]); res["queries"][key][cfg] = r
    size0 = os.path.getsize(path)
    t = time.perf_counter()
    con.executescript("""CREATE INDEX ix_f_date ON fact_sales(date_key); CREATE INDEX ix_f_prod ON fact_sales(product_key);
      CREATE INDEX ix_f_store ON fact_sales(store_key); CREATE INDEX ix_f_cust ON fact_sales(customer_key);
      CREATE INDEX ix_f_promo ON fact_sales(promo_key);""")
    # covering index so that the aggregate over the fact table can be answered from the index
    con.execute("CREATE INDEX ix_f_cover ON fact_sales(date_key, store_key, product_key, net_amount)")
    con.commit(); res["index_build_s"] = round(time.perf_counter() - t, 2)
    size1 = os.path.getsize(path); res["index_mb"] = round((size1 - size0) / 1e6, 2)
    con.execute("DROP TABLE IF EXISTS agg_sales"); t = time.perf_counter()
    con.executescript("""CREATE TABLE agg_sales AS SELECT d.year, d.year_quarter, d.year_month, d.month_num, d.is_weekend,
        p.department, p.category, s.region, s.state, SUM(f.quantity) qty, SUM(f.net_amount) net_sales, COUNT(*) line_count
        FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key JOIN dim_product p ON p.product_key=f.product_key
        JOIN dim_store s ON s.store_key=f.store_key GROUP BY 1,2,3,4,5,6,7,8,9;
        CREATE INDEX ix_agg ON agg_sales(year, month_num);""")
    con.commit(); res["agg_build_s"] = round(time.perf_counter() - t, 2)
    res["agg_rows"] = con.execute("SELECT COUNT(*) FROM agg_sales").fetchone()[0]
    res["agg_mb"] = round((os.path.getsize(path) - size1) / 1e6, 2)
    for key, qd in Q.items():
        r = run(con, qd["star"]); r["rows_scanned"] = scanned(con, r["plan"], qd["star"]); res["queries"][key]["star_idx"] = r
        r = run(con, qd["agg"]); r["rows_scanned"] = scanned(con, r["plan"], qd["agg"]); res["queries"][key]["agg"] = r
        tots = {c: res["queries"][key][c]["total"] for c in ("oltp", "star", "star_idx", "agg")}
        res["queries"][key]["totals_match"] = len({round(v, 0) for v in tots.values()}) == 1
    res["fact_rows"] = con.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    json.dump(res, open(path.replace(".db", "_bench.json"), "w"), indent=1)
    for k, v in res["queries"].items():
        print(k, {c: (v[c]["time_s"], v[c]["rows_scanned"]) for c in ("oltp", "star", "star_idx", "agg")}, "match", v["totals_match"])
    print({k: res[k] for k in ("index_build_s", "index_mb", "agg_build_s", "agg_rows", "agg_mb")})


if __name__ == "__main__":
    main(sys.argv[1])

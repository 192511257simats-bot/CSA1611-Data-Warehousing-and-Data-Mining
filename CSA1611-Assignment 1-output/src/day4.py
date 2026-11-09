"""day4.py - Task 11 Day-4 Design Challenge: evaluate the ORIGINAL design (Type-1 customer, full agg rebuild) against the
online channel (20,000 orders/day ~ 60,000 lines/day), then test the REVISED design (SCD-2 customer, channel and
delivery-partner dimensions, product-code crosswalk, hourly micro-batch + incremental aggregate merge).
Usage: python day4.py fc_1000000.db   (works on a COPY: fc_1000000_d4.db)"""
import sqlite3, sys, shutil, time, datetime as dt
import numpy as np, pandas as pd

src = sys.argv[1]; path = src.replace(".db", "_d4.db"); shutil.copy(src, path)
con = sqlite3.connect(path); c = con.cursor(); rng = np.random.default_rng(11)
T = lambda: time.perf_counter()
print("=== A. TEST ORIGINAL DESIGN: customer address / tier changes (Type-1 overwrite) ===")
o = pd.read_sql("SELECT o.customer_id, o.order_date, SUM(l.qty*l.unit_price-l.discount) net FROM orders o JOIN order_lines l "
                "ON l.order_id=o.order_id GROUP BY o.order_id", con)
cust = pd.read_sql("SELECT cu.customer_id, st.state_name state, cu.loyalty_tier tier FROM customers cu JOIN cities ci USING(city_id) JOIN states st USING(state_id)", con)
states = sorted(cust.state.unique()); tiers = ["Bronze", "Silver", "Gold", "Platinum"]
mv = rng.random(len(cust)) < 0.08; tr = rng.random(len(cust)) < 0.12          # 8% move state, 12% change tier (assumption)
cust["old_state"] = np.where(mv, [rng.choice([s for s in states if s != x]) for x in cust.state], cust.state)  # state BEFORE the move
cust["old_tier"] = np.where(tr, [rng.choice([t for t in tiers if t != x]) for x in cust.tier], cust.tier)
cust["change_date"] = [(dt.date(2025, 4, 1) + dt.timedelta(int(d))).isoformat() for d in rng.integers(0, 500, len(cust))]
o = o.merge(cust, on="customer_id")
true_state = np.where(o.order_date < o.change_date, o.old_state, o.state)            # SCD-2 (as-of-order) answer
true_tier = np.where(o.order_date < o.change_date, o.old_tier, o.tier)               # Type-1 answer = o.state / o.tier (current)
ms = o.net[true_state != o.state].sum() / o.net.sum(); mt = o.net[true_tier != o.tier].sum() / o.net.sum()
print(f"customers that moved: {mv.sum()} ({mv.mean():.1%}); changed tier: {tr.sum()} ({tr.mean():.1%})")
print(f"net sales attributed to the WRONG state by Type-1 : {ms:.2%}")
print(f"net sales attributed to the WRONG loyalty tier     : {mt:.2%}")
by = pd.DataFrame({"type1_state_sales": o.groupby("state").net.sum(), "asof_state_sales": o.groupby(true_state).net.sum()})
by["error_%"] = ((by.type1_state_sales / by.asof_state_sales - 1) * 100).round(2); print(by.round(0).to_string())

print("\n=== B. REVISED DESIGN: structural changes (DDL applied to the warehouse copy) ===")
t = T()
con.executescript("""
CREATE TABLE dim_customer_scd2 AS SELECT customer_key, customer_id, customer_name, city, state, segment, loyalty_tier,
   '2025-01-01' AS valid_from, '9999-12-31' AS valid_to, 1 AS is_current FROM dim_customer;
CREATE UNIQUE INDEX ux_cs_nat ON dim_customer_scd2(customer_id, valid_from);
CREATE TABLE dim_channel(channel_key INTEGER PRIMARY KEY, channel_name TEXT);
INSERT INTO dim_channel VALUES(1,'In-store'),(2,'Online');
CREATE TABLE dim_delivery_partner(partner_key INTEGER PRIMARY KEY, partner_name TEXT, partner_type TEXT);
INSERT INTO dim_delivery_partner VALUES(0,'Not applicable','None'),(1,'SwiftDrop','3PL'),(2,'QuickBox','3PL'),(3,'FreshCart Fleet','Own');
CREATE TABLE product_xref(source_system TEXT, source_code TEXT, product_key INT, PRIMARY KEY(source_system, source_code));
INSERT INTO product_xref SELECT 'ONLINE','ONL-'||printf('%05d',product_id), product_key FROM dim_product;
INSERT INTO dim_store(store_id,store_name,city,state,region) VALUES(999,'Online-Hub-01','Chennai','Tamil Nadu','South');
ALTER TABLE fact_sales ADD COLUMN channel_key INT DEFAULT 1;
ALTER TABLE fact_sales ADD COLUMN partner_key INT DEFAULT 0;
CREATE TABLE agg_sales_v2 AS SELECT year, year_quarter, year_month, month_num, is_weekend, department, category, region, state,
   1 AS channel_key, qty, net_sales, line_count FROM agg_sales;
CREATE UNIQUE INDEX ux_agg2 ON agg_sales_v2(year_month,is_weekend,department,category,region,state,channel_key);
""")
con.commit(); print(f"DDL + backfill (channel=1 default) time: {T()-t:.2f}s")


def micro_batch(n_lines, hour):
    """One hourly micro-batch: stage -> SCD-2 apply -> surrogate lookup/load -> incremental aggregate merge."""
    t0 = T(); day = "2026-11-08"
    cid = rng.integers(1, 20001, n_lines); pc = [f"ONL-{p:05d}" for p in rng.integers(1, 50001, n_lines)]
    qty = rng.integers(1, 5, n_lines); pr = np.round(np.exp(rng.normal(4.8, .9, n_lines)).clip(10, 3000), 2)
    ts = [f"{day} {hour:02d}:{m:02d}:00" for m in rng.integers(0, 60, n_lines)]; part = rng.integers(1, 4, n_lines)
    c.execute("DROP TABLE IF EXISTS stg"); c.execute("CREATE TABLE stg(customer_id INT, pcode TEXT, qty INT, price REAL, ts TEXT, partner INT)")
    c.executemany("INSERT INTO stg VALUES(?,?,?,?,?,?)", zip(cid.tolist(), pc, qty.tolist(), pr.tolist(), ts, part.tolist()))
    t1 = T()
    # SCD-2: ~2% of the customers in this batch changed address/tier -> close the current row, insert a new version
    chg = rng.choice(np.unique(cid), max(1, int(.02 * len(np.unique(cid)))), replace=False).tolist()
    for cu in chg:
        c.execute("UPDATE dim_customer_scd2 SET valid_to=?, is_current=0 WHERE customer_id=? AND is_current=1", (f"{day} {hour:02d}:30:00", cu))
        c.execute("""INSERT INTO dim_customer_scd2 SELECT (SELECT MAX(customer_key)+1 FROM dim_customer_scd2), customer_id, customer_name,
                  city, state, segment, CASE loyalty_tier WHEN 'Bronze' THEN 'Silver' ELSE 'Gold' END, ?, '9999-12-31', 1
                  FROM dim_customer_scd2 WHERE customer_id=? ORDER BY valid_from DESC LIMIT 1""", (f"{day} {hour:02d}:30:00", cu))
    t2 = T()
    c.execute("""INSERT INTO fact_sales(date_key,product_key,store_key,customer_key,promo_key,order_id,line_no,quantity,gross_amount,
                 discount_amount,net_amount,channel_key,partner_key)
      SELECT 20261108, x.product_key, (SELECT store_key FROM dim_store WHERE store_id=999), cs.customer_key, 1, 0, 0, g.qty,
             g.qty*g.price, 0, g.qty*g.price, 2, g.partner
      FROM stg g JOIN product_xref x ON x.source_system='ONLINE' AND x.source_code=g.pcode
      JOIN dim_customer_scd2 cs ON cs.customer_id=g.customer_id AND g.ts>=cs.valid_from AND g.ts<cs.valid_to""")
    t3 = T()
    c.execute("""INSERT INTO agg_sales_v2(year,year_quarter,year_month,month_num,is_weekend,department,category,region,state,channel_key,qty,net_sales,line_count)
      SELECT 2026,'2026-Q4','2026-11',11,1,p.department,p.category,'South','Tamil Nadu',2,SUM(f.quantity),SUM(f.net_amount),COUNT(*)
      FROM fact_sales f JOIN dim_product p ON p.product_key=f.product_key WHERE f.rowid > (SELECT MAX(rowid)-? FROM fact_sales)
      GROUP BY p.department,p.category
      ON CONFLICT(year_month,is_weekend,department,category,region,state,channel_key)
      DO UPDATE SET qty=qty+excluded.qty, net_sales=net_sales+excluded.net_sales, line_count=line_count+excluded.line_count""", (n_lines,))
    con.commit(); t4 = T()
    return dict(lines=n_lines, stage=t1 - t0, scd2=t2 - t1, fact_load=t3 - t2, agg_merge=t4 - t3, total=t4 - t0, scd_changes=len(chg))


print("\n=== C. HOURLY MICRO-BATCH at the 1,000,000-row base (avg hour = 2,500 lines; peak hour = 7,500 lines) ===")
res = []
for n in (2500, 7500):
    r = micro_batch(n, 14 if n == 2500 else 15); res.append(r)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
t = T(); c.execute("DROP TABLE IF EXISTS agg_full"); c.execute(
    """CREATE TABLE agg_full AS SELECT d.year, d.year_quarter, d.year_month, d.month_num, d.is_weekend, p.department, p.category, s.region, s.state,
       f.channel_key, SUM(f.quantity) qty, SUM(f.net_amount) net_sales, COUNT(*) line_count FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
       JOIN dim_product p ON p.product_key=f.product_key JOIN dim_store s ON s.store_key=f.store_key GROUP BY 1,2,3,4,5,6,7,8,9,10""")
full1 = T() - t; n1 = c.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
print(f"FULL aggregate rebuild at {n1:,} fact rows (original refresh method): {full1:.2f}s")

print("\n=== D. SCALE TEST: add ~1.8M rows (one month of online sales) then compare refresh methods ===")
c.execute("INSERT INTO fact_sales SELECT * FROM fact_sales LIMIT 1000000"); c.execute("INSERT INTO fact_sales SELECT * FROM fact_sales LIMIT 800000"); con.commit()
n2 = c.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
t = T(); c.execute("DROP TABLE agg_full")
c.execute("""CREATE TABLE agg_full AS SELECT d.year, d.year_quarter, d.year_month, d.month_num, d.is_weekend, p.department, p.category, s.region, s.state,
       f.channel_key, SUM(f.quantity) qty, SUM(f.net_amount) net_sales, COUNT(*) line_count FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
       JOIN dim_product p ON p.product_key=f.product_key JOIN dim_store s ON s.store_key=f.store_key GROUP BY 1,2,3,4,5,6,7,8,9,10"""); full2 = T() - t
r = micro_batch(2500, 16)
print(f"fact rows = {n2:,}: FULL rebuild {full2:.2f}s  vs  INCREMENTAL hourly batch {r['total']:.3f}s  (speed-up x{full2 / r['total']:.0f})")
print(f"projection: 20,000 orders/day x 3 lines x 365 = {20000*3*365:,} rows/yr -> full rebuild ~ {full2 / n2 * (n2 + 21_900_000):.0f}s by year-end (linear)")

print("\n=== E. QUERY: sales by state and loyalty tier AS OF ORDER DATE (revised design) ===")
t = T(); rows = c.execute("""SELECT cs.state, cs.loyalty_tier, ROUND(SUM(f.net_amount),0) FROM fact_sales f JOIN dim_customer_scd2 cs
   ON cs.customer_key=f.customer_key WHERE f.channel_key=2 GROUP BY 1,2 ORDER BY 1,2 LIMIT 6""").fetchall()
print(f"query time {T()-t:.2f}s (online rows only):", rows[:4])
nrows = c.execute("SELECT COUNT(*) FROM dim_customer_scd2").fetchone()[0]
print(f"\nSCD-2 customer dimension grew from 20,000 to {nrows:,} rows after the 3 simulated hourly batches")
print("storage: 2 new int columns x 21.9M rows/yr = %.0f MB/yr; SCD-2 growth at 1,000 changes/month x 90 B = %.2f MB/yr" % (2 * 4 * 21.9, 12000 * 90 / 1e6))

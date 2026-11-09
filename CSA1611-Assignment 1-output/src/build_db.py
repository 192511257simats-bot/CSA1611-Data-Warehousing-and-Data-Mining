"""build_db.py - FreshCart: generate synthetic OLTP data and load the star schema (ETL).
Usage: python build_db.py <fact_rows> <db_path>
Data-generation method: dimension sizes follow Task 4 (50,000 products, 800 brands, 60 categories,
12 departments, 120 stores, 70 cities, 6 states, 3 regions); sales lines are drawn with a fixed seed:
Zipf-like product popularity, 1.4x weight on weekends, 25% of orders carry a promotion (5-20% off)."""
import sqlite3, sys, time, os, json, datetime as dt
import numpy as np

OLTP_DDL = """
CREATE TABLE regions(region_id INTEGER PRIMARY KEY, region_name TEXT);
CREATE TABLE states(state_id INTEGER PRIMARY KEY, state_name TEXT, region_id INT);
CREATE TABLE cities(city_id INTEGER PRIMARY KEY, city_name TEXT, state_id INT);
CREATE TABLE stores(store_id INTEGER PRIMARY KEY, store_code TEXT, city_id INT);
CREATE TABLE departments(department_id INTEGER PRIMARY KEY, department_name TEXT);
CREATE TABLE categories(category_id INTEGER PRIMARY KEY, category_name TEXT, department_id INT);
CREATE TABLE brands(brand_id INTEGER PRIMARY KEY, brand_name TEXT, category_id INT);
CREATE TABLE products(product_id INTEGER PRIMARY KEY, product_name TEXT, brand_id INT, list_price REAL);
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY, customer_name TEXT, city_id INT, segment TEXT, loyalty_tier TEXT);
CREATE TABLE promotions(promo_id INTEGER PRIMARY KEY, promo_name TEXT, promo_type TEXT, discount_pct REAL);
CREATE TABLE orders(order_id INTEGER PRIMARY KEY, customer_id INT, store_id INT, order_date TEXT, promo_id INT);
CREATE TABLE order_lines(order_id INT, line_no INT, product_id INT, qty INT, unit_price REAL, discount REAL,
                         PRIMARY KEY(order_id, line_no));
CREATE TABLE returns(return_id INTEGER PRIMARY KEY, order_id INT, line_no INT, return_date TEXT, qty INT,
                     refund REAL, reason TEXT);
"""
STAR_DDL = """
CREATE TABLE dim_date(date_key INTEGER PRIMARY KEY, full_date TEXT, day_of_week TEXT, is_weekend INT,
  month_num INT, month_name TEXT, year_month TEXT, quarter_num INT, year_quarter TEXT, year INT);
CREATE TABLE dim_product(product_key INTEGER PRIMARY KEY, product_id INT, product_name TEXT, brand TEXT,
  category TEXT, department TEXT, list_price REAL);
CREATE TABLE dim_store(store_key INTEGER PRIMARY KEY, store_id INT, store_name TEXT, city TEXT, state TEXT, region TEXT);
CREATE TABLE dim_customer(customer_key INTEGER PRIMARY KEY, customer_id INT, customer_name TEXT, city TEXT,
  state TEXT, segment TEXT, loyalty_tier TEXT);
CREATE TABLE dim_promotion(promo_key INTEGER PRIMARY KEY, promo_id INT, promo_name TEXT, promo_type TEXT, discount_pct REAL);
CREATE TABLE fact_sales(date_key INT, product_key INT, store_key INT, customer_key INT, promo_key INT,
  order_id INT, line_no INT, quantity INT, gross_amount REAL, discount_amount REAL, net_amount REAL);
CREATE TABLE fact_returns(date_key INT, product_key INT, store_key INT, customer_key INT,
  order_id INT, line_no INT, return_qty INT, refund_amount REAL, reason TEXT);
"""
DEPTS = {"Grocery": ["Rice & Grains", "Oils", "Pulses", "Spices", "Sugar & Salt"],
 "Dairy": ["Milk", "Curd", "Cheese", "Butter", "Paneer"], "Bakery": ["Bread", "Cakes", "Biscuits", "Buns", "Cookies"],
 "Produce": ["Fruits", "Vegetables", "Herbs", "Organic", "Exotic"], "Beverages": ["Tea", "Coffee", "Juices", "Soft Drinks", "Water"],
 "Snacks": ["Chips", "Namkeen", "Chocolates", "Nuts", "Popcorn"], "Personal Care": ["Soap", "Shampoo", "Skin Care", "Oral Care", "Deodorant"],
 "Household": ["Detergent", "Cleaners", "Tissues", "Utensils", "Fresheners"], "Frozen": ["Ice Cream", "Frozen Veg", "Ready Meals", "Frozen Snacks", "Frozen Meat"],
 "Meat & Fish": ["Chicken", "Mutton", "Fish", "Eggs", "Prawns"], "Baby Care": ["Diapers", "Baby Food", "Baby Soap", "Wipes", "Toys"],
 "Electronics": ["Batteries", "Bulbs", "Chargers", "Earphones", "Cables"]}
STATES = [("Tamil Nadu", 1, ["Chennai", "Coimbatore", "Madurai"]), ("Telangana", 1, ["Hyderabad", "Warangal"]),
          ("Maharashtra", 2, ["Pune", "Mumbai", "Nagpur"]), ("Gujarat", 2, ["Ahmedabad", "Surat"]),
          ("Delhi", 3, ["New Delhi"]), ("Uttar Pradesh", 3, ["Lucknow", "Kanpur"])]
SEGMENTS = ["Premium", "Regular", "Occasional", "New"]; TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
START, END = dt.date(2025, 1, 1), dt.date(2026, 10, 31)


def build(n, path):
    if os.path.exists(path): os.remove(path)
    rd = np.random.default_rng(42)           # dimension generator
    con = sqlite3.connect(path); c = con.cursor(); c.executescript(OLTP_DDL + STAR_DDL)
    c.executemany("INSERT INTO regions VALUES(?,?)", [(1, "South"), (2, "West"), (3, "North")])
    cities, k = [], 1
    for si, (sn, rid, names) in enumerate(STATES, 1):
        c.execute("INSERT INTO states VALUES(?,?,?)", (si, sn, rid))
    quota = [12, 12, 12, 12, 11, 11]          # 70 cities in total
    for si, (sn, rid, names) in enumerate(STATES, 1):
        for j in range(quota[si - 1]):
            cities.append((k, names[j] if j < len(names) else f"{sn[:3]} Town {j}", si)); k += 1
    c.executemany("INSERT INTO cities VALUES(?,?,?)", cities)
    cnt = {}
    stores = []
    for i in range(120):
        cid = i % 70 + 1; cnt[cid] = cnt.get(cid, 0) + 1
        stores.append((i + 1, f"{cities[cid-1][1]}-{cnt[cid]:02d}", cid))
    c.executemany("INSERT INTO stores VALUES(?,?,?)", stores)
    cat_id = br = 0; cats, brands = [], []
    c.executemany("INSERT INTO departments VALUES(?,?)", [(i + 1, d) for i, d in enumerate(DEPTS)])
    for di, (d, cl) in enumerate(DEPTS.items(), 1):
        for cn in cl:
            cat_id += 1; cats.append((cat_id, cn, di))
    c.executemany("INSERT INTO categories VALUES(?,?,?)", cats)
    brands = [(b + 1, f"Brand{b+1:03d}", b % 60 + 1) for b in range(800)]
    c.executemany("INSERT INTO brands VALUES(?,?,?)", brands)
    price = np.round(np.exp(rd.normal(4.8, 0.9, 50000)).clip(10, 3000), 2)
    cn = {x[0]: x[1] for x in cats}; bcat = {b[0]: b[2] for b in brands}
    prods = [(p + 1, f"{cn[bcat[p % 800 + 1]]} Item {p+1:05d}", p % 800 + 1, float(price[p])) for p in range(50000)]
    c.executemany("INSERT INTO products VALUES(?,?,?,?)", prods)
    NC = 20000
    seg = rd.choice(SEGMENTS, NC, p=[.15, .45, .30, .10]); tier = rd.choice(TIERS, NC, p=[.5, .3, .15, .05])
    c.executemany("INSERT INTO customers VALUES(?,?,?,?,?)",
                  [(i + 1, f"Customer {i+1:05d}", int(rd.integers(1, 71)), seg[i], tier[i]) for i in range(NC)])
    promos = [(0, "No Promotion", "None", 0.0)] + [(i, f"Promo {i:02d}", ["Festival", "Bundle", "Loyalty", "Clearance"][i % 4], float(5 + (i * 3) % 16)) for i in range(1, 26)]
    c.executemany("INSERT INTO promotions VALUES(?,?,?,?)", promos)
    # ---------- fact data (OLTP side) ----------
    r = np.random.default_rng(7 + n)
    sizes = r.integers(1, 6, size=n); sizes = sizes[:np.searchsorted(np.cumsum(sizes), n) + 1]
    sizes[-1] -= sizes.sum() - n; sizes = sizes[sizes > 0]
    m = len(sizes)
    days = [START + dt.timedelta(d) for d in range((END - START).days + 1)]
    w = np.array([1.4 if d.weekday() >= 5 else 1.0 for d in days]); w /= w.sum()
    odate = r.choice(len(days), m, p=w)
    promo = np.where(r.random(m) < .25, r.integers(1, 26, m), 0)
    orders = list(zip(range(1, m + 1), r.integers(1, NC + 1, m).tolist(), r.integers(1, 121, m).tolist(),
                      [days[i].isoformat() for i in odate], promo.tolist()))
    c.executemany("INSERT INTO orders VALUES(?,?,?,?,?)", orders)
    pw = 1 / np.arange(1, 50001) ** 0.8; pw /= pw.sum()
    pid = r.choice(50000, n, p=pw) + 1
    qty = r.choice([1, 2, 3, 4, 5, 6], n, p=[.4, .25, .15, .1, .06, .04])
    oid = np.repeat(np.arange(1, len(sizes) + 1), sizes)
    lno = np.concatenate([np.arange(1, s + 1) for s in sizes])
    up = price[pid - 1]; dpct = np.array([p[3] for p in promos])[promo][oid - 1] / 100
    disc = np.round(qty * up * dpct, 2)
    c.executemany("INSERT INTO order_lines VALUES(?,?,?,?,?,?)",
                  zip(oid.tolist(), lno.tolist(), pid.tolist(), qty.tolist(), up.tolist(), disc.tolist()))
    ridx = r.choice(n, int(n * .03), replace=False)
    odt = np.array([o[3] for o in orders])
    rets = [(i + 1, int(oid[j]), int(lno[j]), odt[oid[j] - 1], 1, float(up[j]), r.choice(["Damaged", "Expired", "Wrong item", "Changed mind"]))
            for i, j in enumerate(ridx)]
    c.executemany("INSERT INTO returns VALUES(?,?,?,?,?,?,?)", rets)
    con.commit()
    # ---------- ETL: OLTP -> star ----------
    t0 = time.time()
    dd = []
    for d in days:
        q = (d.month + 2) // 3
        dd.append((int(d.strftime("%Y%m%d")), d.isoformat(), d.strftime("%A"), int(d.weekday() >= 5), d.month, d.strftime("%B"),
                   d.strftime("%Y-%m"), q, f"{d.year}-Q{q}", d.year))
    c.executemany("INSERT INTO dim_date VALUES(?,?,?,?,?,?,?,?,?,?)", dd)
    c.executescript("""
    INSERT INTO dim_product(product_id,product_name,brand,category,department,list_price)
      SELECT p.product_id,p.product_name,b.brand_name,c.category_name,d.department_name,p.list_price
      FROM products p JOIN brands b USING(brand_id) JOIN categories c USING(category_id) JOIN departments d USING(department_id);
    INSERT INTO dim_store(store_id,store_name,city,state,region)
      SELECT s.store_id,s.store_code,ci.city_name,st.state_name,r.region_name
      FROM stores s JOIN cities ci USING(city_id) JOIN states st USING(state_id) JOIN regions r USING(region_id);
    INSERT INTO dim_customer(customer_id,customer_name,city,state,segment,loyalty_tier)
      SELECT cu.customer_id,cu.customer_name,ci.city_name,st.state_name,cu.segment,cu.loyalty_tier
      FROM customers cu JOIN cities ci USING(city_id) JOIN states st USING(state_id);
    INSERT INTO dim_promotion(promo_id,promo_name,promo_type,discount_pct) SELECT * FROM promotions;
    CREATE UNIQUE INDEX ux_dd ON dim_date(full_date); CREATE UNIQUE INDEX ux_dp ON dim_product(product_id);
    CREATE UNIQUE INDEX ux_ds ON dim_store(store_id); CREATE UNIQUE INDEX ux_dc ON dim_customer(customer_id);
    CREATE UNIQUE INDEX ux_dpr ON dim_promotion(promo_id);
    INSERT INTO fact_sales
      SELECT d.date_key,p.product_key,s.store_key,cu.customer_key,pr.promo_key,l.order_id,l.line_no,l.qty,
             l.qty*l.unit_price,l.discount,l.qty*l.unit_price-l.discount
      FROM order_lines l JOIN orders o ON o.order_id=l.order_id JOIN dim_date d ON d.full_date=o.order_date
      JOIN dim_product p ON p.product_id=l.product_id JOIN dim_store s ON s.store_id=o.store_id
      JOIN dim_customer cu ON cu.customer_id=o.customer_id JOIN dim_promotion pr ON pr.promo_id=o.promo_id;
    INSERT INTO fact_returns
      SELECT d.date_key,p.product_key,s.store_key,cu.customer_key,r.order_id,r.line_no,r.qty,r.refund,r.reason
      FROM returns r JOIN orders o ON o.order_id=r.order_id JOIN order_lines l ON l.order_id=r.order_id AND l.line_no=r.line_no
      JOIN dim_date d ON d.full_date=r.return_date JOIN dim_product p ON p.product_id=l.product_id
      JOIN dim_store s ON s.store_id=o.store_id JOIN dim_customer cu ON cu.customer_id=o.customer_id;
    """)
    con.commit(); etl = time.time() - t0
    nf = c.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    info = dict(fact_rows=nf, orders=m, etl_load_s=round(etl, 2), db_mb=round(os.path.getsize(path) / 1e6, 1))
    json.dump(info, open(path.replace(".db", "_build.json"), "w"))
    print(info); con.close()


if __name__ == "__main__":
    build(int(sys.argv[1]), sys.argv[2])

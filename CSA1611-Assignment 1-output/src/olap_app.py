"""olap_app.py - Task 7: interactive OLAP application on the FreshCart star schema.
Usage: python olap_app.py fc_100000.db      (all choices are typed by the user - nothing is hard-coded)
Every result is RECONCILED against an independent query on the normalised OLTP tables."""
import sqlite3, sys
import pandas as pd

HIER = {  # coarse -> fine ; 'ALL' = dimension aggregated away (apex level)
 "time":     ["ALL", "year", "quarter", "month", "day"],
 "product":  ["ALL", "department", "category", "product"],
 "store":    ["ALL", "region", "state", "city", "store"],
 "customer": ["ALL", "segment"]}
STAR = {  # (table alias, column) in the star schema
 ("time", "year"): "d.year", ("time", "quarter"): "d.year_quarter", ("time", "month"): "d.year_month", ("time", "day"): "d.full_date",
 ("product", "department"): "p.department", ("product", "category"): "p.category", ("product", "product"): "p.product_name",
 ("store", "region"): "s.region", ("store", "state"): "s.state", ("store", "city"): "s.city", ("store", "store"): "s.store_name",
 ("customer", "segment"): "c.segment"}
OLTP = {  # same attribute computed independently from the normalised tables
 ("time", "year"): "CAST(strftime('%Y',o.order_date) AS INT)",
 ("time", "quarter"): "strftime('%Y',o.order_date)||'-Q'||((CAST(strftime('%m',o.order_date) AS INT)+2)/3)",
 ("time", "month"): "substr(o.order_date,1,7)", ("time", "day"): "o.order_date",
 ("product", "department"): "dp.department_name", ("product", "category"): "ca.category_name", ("product", "product"): "p.product_name",
 ("store", "region"): "r.region_name", ("store", "state"): "st.state_name", ("store", "city"): "ci.city_name", ("store", "store"): "s.store_code",
 ("customer", "segment"): "cu.segment"}
STAR_FROM = {"time": "JOIN dim_date d ON d.date_key=f.date_key", "product": "JOIN dim_product p ON p.product_key=f.product_key",
             "store": "JOIN dim_store s ON s.store_key=f.store_key", "customer": "JOIN dim_customer c ON c.customer_key=f.customer_key"}
OLTP_FROM = """FROM order_lines l JOIN orders o ON o.order_id=l.order_id JOIN products p ON p.product_id=l.product_id
 JOIN brands b ON b.brand_id=p.brand_id JOIN categories ca ON ca.category_id=b.category_id JOIN departments dp ON dp.department_id=ca.department_id
 JOIN stores s ON s.store_id=o.store_id JOIN cities ci ON ci.city_id=s.city_id JOIN states st ON st.state_id=ci.state_id
 JOIN regions r ON r.region_id=st.region_id JOIN customers cu ON cu.customer_id=o.customer_id"""


def build_sql(levels, filters, star=True):
    cols, where, params, dims = [], [], [], set()
    M = STAR if star else OLTP
    for dim, lv in levels.items():
        if lv != "ALL": cols.append(M[(dim, lv)]); dims.add(dim)
    for dim, lv, vals in filters:
        where.append(f"{M[(dim, lv)]} IN ({','.join('?' * len(vals))})"); params += vals; dims.add(dim)
    sel = ", ".join(cols + ["SUM(" + ("f.net_amount" if star else "l.qty*l.unit_price-l.discount") + ")",
                            "SUM(" + ("f.quantity" if star else "l.qty") + ")"])
    frm = ("FROM fact_sales f " + " ".join(STAR_FROM[d] for d in dims)) if star else OLTP_FROM
    sql = f"SELECT {sel} {frm}" + (" WHERE " + " AND ".join(where) if where else "") + \
          (" GROUP BY " + ", ".join(str(i + 1) for i in range(len(cols))) if cols else "") + (" ORDER BY " + ", ".join(str(i + 1) for i in range(len(cols))) if cols else "")
    return sql, params, [c.split(".")[1] for c in cols]


def evaluate(con, levels, filters):
    sql, p, names = build_sql(levels, filters, True)
    rows = con.execute(sql, p).fetchall()
    sql2, p2, _ = build_sql(levels, filters, False)
    chk = con.execute(sql2, p2).fetchall()
    ok = len(rows) == len(chk) and all(a[:-2] == b[:-2] and abs(a[-2] - b[-2]) < 0.01 and a[-1] == b[-1] for a, b in zip(rows, chk))
    df = pd.DataFrame(rows, columns=names + ["net_sales", "qty"])
    return df, ok, sql


def show(con, levels, filters):
    df, ok, sql = evaluate(con, levels, filters)
    print("\nCuboid:", {d: l for d, l in levels.items()}, "| filters:", [(d, l, v) for d, l, v in filters] or "none")
    print(df.head(10).to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
    print(f"[{len(df)} rows] grand total net_sales = {df.net_sales.sum():,.2f}")
    print("RECONCILIATION with OLTP source:", "PASS" if ok else "FAIL")
    return df


def inp(prompt):
    v = input(prompt)
    if not sys.stdin.isatty(): print(v)          # echo typed answers when input is piped (for the screenshots)
    return v


def ask(prompt, choices):
    while True:
        v = inp(f"{prompt} {choices}: ").strip()
        if v in choices: return v
        print("  invalid choice, try again")


def main(path):
    con = sqlite3.connect(path)
    levels = {"time": "year", "product": "department", "store": "region", "customer": "ALL"}; filters = []
    print(f"FreshCart OLAP - {path}: {con.execute('SELECT COUNT(*) FROM fact_sales').fetchone()[0]:,} fact rows")
    while True:
        print("\n1 Show  2 Roll-up  3 Drill-down  4 Slice  5 Dice  6 Pivot  7 Reset  0 Quit")
        ch = inp("operation: ").strip()
        if ch == "0": break
        if ch == "7": levels = {"time": "year", "product": "department", "store": "region", "customer": "ALL"}; filters = []
        if ch in ("2", "3"):
            d = ask("dimension", list(HIER)); H = HIER[d]; i = H.index(levels[d])
            j = max(0, i - 1) if ch == "2" else min(len(H) - 1, i + 1)
            print(f"  {d}: {levels[d]} -> {H[j]}"); levels[d] = H[j]
        if ch in ("4", "5"):
            d = ask("dimension", list(HIER)); lv = ask("level", HIER[d][1:])
            vals = [v.strip() for v in inp("value" + (" (one)" if ch == "4" else "s (comma separated)") + ": ").split(",")]
            if lv == "year": vals = [int(v) for v in vals]
            if ch == "4": vals = vals[:1]
            filters.append((d, lv, vals))
            if levels[d] == "ALL": levels[d] = lv
        if ch == "6":
            show_levels = [d for d, l in levels.items() if l != "ALL"]
            rd = ask("row dimension", show_levels); cd = ask("column dimension", [d for d in show_levels if d != rd])
            others = {d: ("ALL" if d not in (rd, cd) else l) for d, l in levels.items()}
            df, ok, _ = evaluate(con, others, filters)
            order = [d for d in others if others[d] != "ALL"]
            print(df.pivot_table(index=df.columns[order.index(rd)], columns=df.columns[order.index(cd)], values="net_sales", aggfunc="sum", fill_value=0).round(0).to_string())
            print("RECONCILIATION with OLTP source:", "PASS" if ok else "FAIL"); continue
        if ch in ("1", "2", "3", "4", "5", "7"): show(con, levels, filters)


if __name__ == "__main__":
    main(sys.argv[1])

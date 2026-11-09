"""etl_task5.py - Task 5: clean the six-row FreshCart extract, resolve surrogate keys, reject bad rows, audit counts,
and demonstrate SCD handling of a customer address change."""
import re, datetime as dt
import pandas as pd

raw = pd.DataFrame([
 [1001, "Rajesh Kumar", "Chennai-04", "Basmati Rice 5kg", "2", "620.00", "03/11/2026"],
 [1002, "R. Kumar", "chennai-04", "Basmati rice 5 kg", "1", "620.00", "2026-11-03"],
 [1003, "Anita Joseph", "Pune-11", "Olive Oil 1L", "-3", "780.00", "04-Nov-26"],
 [1004, "Meena S", None, "Tea 250g", "4", "95.50", "04/11/2026"],
 [1005, "Anita Joseph", "Pune-11", "Olive Oil 1L", "3", "9.40 (USD)", "04/11/2026"],
 [1006, "Vikram Rao", "Hyd-02", None, "1", "1,250", "05/11/2026"]],
 columns=["order_id", "customer", "store", "product", "qty", "unit_price", "order_date"])
USD_INR = 83.00                                    # assumed rate from the rate table (documented assumption)
STORE_FIX = {"hyd": "Hyderabad"}                   # abbreviation lookup
CUST_MASTER = {"rajesh kumar": 501, "anita joseph": 502, "meena s": 503, "vikram rao": 504}
PROD_MASTER = {"basmati rice 5kg": 9001, "olive oil 1l": 9002, "tea 250g": 9003}


CANON = {9001: "Basmati Rice 5kg", 9002: "Olive Oil 1L", 9003: "Tea 250g"}


def to_date(s):  # Rule: accept dd/mm/yyyy, yyyy-mm-dd, dd-Mon-yy -> ISO yyyy-mm-dd
    for f in ("%d/%m/%Y", "%Y-%m-%d", "%d-%b-%y"):
        try: return dt.datetime.strptime(s, f).date().isoformat()
        except ValueError: pass
    return None


def price(s):    # Rule: strip separators, convert USD -> INR
    s = s.replace(",", "")
    return round(float(re.sub(r"[^\d.]", "", s)) * (USD_INR if "USD" in s else 1), 2)


def cust(n):     # Rule: "R. Kumar" -> match surname + initial against master (flag for steward review)
    k = n.lower()
    if k in CUST_MASTER: return CUST_MASTER[k], ""
    first, last = n.split(".")[0].strip().lower(), n.split()[-1].lower()
    for m, key in CUST_MASTER.items():
        if m.split()[-1] == last and m.startswith(first[0]): return key, "fuzzy-match"
    return -1, "unknown-customer"


rows, rejects = [], []
for _, r in raw.iterrows():
    flags = []
    ck, f = cust(r.customer); flags += [f] if f else []
    store = r.store
    if pd.isna(store): skey, store, flags = -1, "Unknown", flags + ["null store -> Unknown member"]
    else:
        city, no = store.split("-"); city = STORE_FIX.get(city.lower(), city).title(); store = f"{city}-{no}"
    prod = None if pd.isna(r["product"]) else re.sub(r"(\d)\s*(kg|g|l)\b", r"\1\2", r["product"].lower()).strip()
    pkey = PROD_MASTER.get(prod, -1) if prod else -1
    if pkey == -1: flags.append("null product -> Unknown member")
    qty = int(r.qty); up = price(r.unit_price)
    if "USD" in r.unit_price: flags.append(f"USD converted @ {USD_INR}")
    if "," in r.unit_price: flags.append("thousand separator removed")
    if qty <= 0:
        rejects.append(dict(order_id=r.order_id, reason="qty <= 0 (possible return) -> route to Returns pipeline")); continue
    rows.append(dict(order_id=r.order_id, customer_key=ck, store=store,
                     product_key=pkey, product=CANON.get(pkey, "Unknown"), qty=qty, unit_price=up, net_amount=round(qty * up, 2),
                     order_date=to_date(r.order_date), dq_flags="; ".join(flags)))
clean = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20); pd.set_option("display.max_colwidth", 40)
print("=== BEFORE (raw extract) ==="); print(raw.to_string(index=False))
print("\n=== AFTER (conformed rows loaded to fact_sales) ==="); print(clean.to_string(index=False))
print("\n=== REJECTED ==="); print(pd.DataFrame(rejects).to_string(index=False))
print(f"\n=== AUDIT === extracted={len(raw)} loaded={len(clean)} rejected={len(rejects)} balanced={len(raw) == len(clean) + len(rejects)}")
print(f"control total (raw qty*price, valid rows) vs loaded net: {clean.net_amount.sum():,.2f}")

# ---- SCD demonstration: customer 501 moves from Chennai to Pune on 2026-11-05 ----
dim = pd.DataFrame([dict(customer_key=1, customer_id=501, city="Chennai", tier="Silver", valid_from="2025-01-01", valid_to="9999-12-31", current=1)])
def scd2(dim, cid, city, tier, eff):
    cur = dim[(dim.customer_id == cid) & (dim.current == 1)].index[0]
    if (dim.loc[cur, "city"], dim.loc[cur, "tier"]) == (city, tier): return dim
    dim.loc[cur, ["valid_to", "current"]] = [eff, 0]
    return pd.concat([dim, pd.DataFrame([dict(customer_key=dim.customer_key.max() + 1, customer_id=cid, city=city, tier=tier,
                                           valid_from=eff, valid_to="9999-12-31", current=1)])], ignore_index=True)
t1 = dim.copy(); t1.loc[0, "city"] = "Pune"
print("\n=== SCD Type 1 (original design: overwrite, no history) ==="); print(t1[["customer_key", "customer_id", "city", "tier"]].to_string(index=False))
print("\n=== SCD Type 2 (Day-4 redesign: new row, history kept) ==="); print(scd2(dim.copy(), 501, "Pune", "Silver", "2026-11-05").to_string(index=False))

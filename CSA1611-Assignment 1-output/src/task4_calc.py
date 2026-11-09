"""task4_calc.py - Task 4: dimension storage, star vs snowflake (byte widths are stated assumptions)."""
W = dict(key=4, sku=12, pname=40, size=10, bname=25, cname=25, dname=25, scode=10, sname=30, city=25, state=25, region=20, mgr=20)
star_prod = 50000 * (W['key'] + W['sku'] + W['pname'] + W['size'] + W['bname'] + W['cname'] + W['dname'])
snow_prod = (50000 * (W['key'] + W['sku'] + W['pname'] + W['size'] + 4)      # product + brand_key
             + 800 * (4 + W['bname'] + 4)                                     # brand(+category_key)
             + 60 * (4 + W['cname'] + 4)                                      # category(+department_key)
             + 12 * (4 + W['dname']))
star_store = 120 * (W['key'] + W['scode'] + W['sname'] + W['city'] + W['state'] + W['region'])
snow_store = 120 * (4 + W['scode'] + W['sname'] + 4) + 70 * (4 + W['city'] + 4) + 6 * (4 + W['state'] + 4) + 3 * (4 + W['region'])
for n, s, w in (("Product dimension", star_prod, snow_prod), ("Store dimension", star_store, snow_store)):
    print(f"{n}: star = {s:,} B ({s/1e6:.3f} MB) | snowflake = {w:,} B ({w/1e6:.3f} MB) | saving = {s-w:,} B ({(s-w)/s:.1%})")
t_s, t_w = star_prod + star_store, snow_prod + snow_store
print(f"TOTAL dims: star {t_s/1e6:.3f} MB, snowflake {t_w/1e6:.3f} MB, saving {(t_s-t_w)/1e6:.3f} MB")
fact = 1_000_000 * (5 * 4 + 4 + 4 + 4 + 8 * 3)   # 5 FKs, order_id, line_no, qty, 3 amounts
print(f"fact table at 1,000,000 rows ~ {fact/1e6:.0f} MB -> snowflake saving is {(t_s-t_w)/fact:.1%} of fact size")
print("Rows: star product=50,000 | snowflake product=50,000 + brand=800 + category=60 + department=12 = 50,872")
print("Rows: star store=120 | snowflake store=120 + city=70 + state=6 + region=3 = 199")
print("Cuboids: with hierarchies = (4+1)(3+1)(3+1)(1+1) = %d ; without = 2^4 = %d" % (5 * 4 * 4 * 2, 2 ** 4))

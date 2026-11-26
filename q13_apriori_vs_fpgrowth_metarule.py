"""Day 4 Exercise - Q13: (a) frequent itemsets with Apriori and FP-Growth, compare efficiency; (b) strong rules matching the metarule
buys(X,item1) ^ buys(X,item2) => buys(X,item3).  min_sup = 60% (3 of 5), min_conf = 80%."""
import sys, time; sys.path.insert(0, "common")
from fpm_utils import *
T = [list("MONKEY"), list("DONKEY"), list("MAKE"), list("MUCKY"), list("COOKIE")]
T = [sorted(set(t)) for t in T]; n = len(T); ms, mc = 3, 0.80
print(f"{n} transactions; min_sup = {ms} (60%), min_conf = {mc:.0%}\n(a) Frequent itemsets")
fa = apriori(T, ms, verbose=False); ff = fp_growth(T, ms)
for s, c in sorted(fa.items(), key=lambda x: (len(x[0]), sorted(x[0]))): print(f"  {fmt(s):15s} {c}")
print("Apriori result == FP-Growth result:", fa == ff)
# efficiency: wall-clock over many repetitions + number of candidate itemsets whose support Apriori had to count
R = 2000
t0 = time.perf_counter(); [apriori(T, ms, verbose=False) for _ in range(R)]; ta = (time.perf_counter() - t0) / R
t0 = time.perf_counter(); [fp_growth(T, ms) for _ in range(R)]; tf = (time.perf_counter() - t0) / R
items = sorted({i for t in T for i in t}); L1 = [i for i in items if sum(i in t for t in T) >= ms]
cands = len(items) + len(list(itertools.combinations(L1, 2)))
print(f"\nEfficiency (average of {R} runs): Apriori = {ta*1e6:.0f} microseconds, FP-Growth = {tf*1e6:.0f} microseconds")
print(f"Apriori scans the database once per level (3 levels here) and had to count {cands} candidate itemsets (11 1-itemsets + 10 2-itemsets);")
print("FP-Growth scans the database only TWICE (count items, build the tree) and never generates candidates.")
faster = "Apriori" if ta < tf else "FP-Growth"
print(f"Measured on this tiny 5-transaction table, {faster} is the faster one ({min(ta, tf)*1e6:.0f} vs {max(ta, tf)*1e6:.0f} microseconds)" +
      (": building trees and conditional bases costs more than a few cheap scans." if faster == "Apriori" else "."))
print("The advantage of FP-Growth appears on large / dense data, where repeated database scans and the candidate explosion dominate the cost of Apriori.")
print("\n(b) Strong rules matching  buys(X, item1) ^ buys(X, item2) => buys(X, item3)   [2 items on the left, 1 on the right]")
rules = [r for r in gen_rules(fa, n, 0.0) if len(r["A"]) == 2 and len(r["B"]) == 1]
print_rules(rules, mc)
print("\nStrong rules:")
for r in rules:
    if r["conf"] >= mc: print(f"  buys(X, {sorted(r['A'])[0]}) ^ buys(X, {sorted(r['A'])[1]}) => buys(X, {sorted(r['B'])[0]})   [support = {r['support']:.0%}, confidence = {r['conf']:.0%}]")

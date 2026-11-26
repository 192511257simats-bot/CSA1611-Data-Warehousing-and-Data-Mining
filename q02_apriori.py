"""Day 5 Assignment - Q2: Construct Apriori (support = 2, confidence = 80%) for the TID 100-500 table (f,a,c,d,g,i,m,p ...)."""
import sys; sys.path.insert(0, "common")
from fpm_utils import *
T = [list("facdgimp"), list("abcflmo"), list("bfhjo"), list("bcksp"), list("afcelpmn")]
n = len(T); print(f"{n} transactions, min_sup = 2 (40%), min_conf = 80%")
freq = apriori(T, 2)
print("\nAll frequent itemsets:", len(freq))
for k in range(1, 6):
    s = [(fmt(i), c) for i, c in sorted(freq.items(), key=lambda x: sorted(x[0])) if len(i) == k]
    if s: print(f"  size {k} ({len(s)}):", ", ".join(f"{a}:{c}" for a, c in s))
rules = gen_rules(freq, n, 0.0); strong = [r for r in rules if r["conf"] >= 0.8 - 1e-12]
print(f"\nAssociation rules with confidence >= 80%: {len(strong)} of {len(rules)} candidate rules")
print_rules(strong)

"""Day 3 - Q2: Market-basket table: (a) max number of association rules, (b) max size of frequent itemsets."""
import itertools
T = [{"Milk","Beer","Diapers"}, {"Bread","Butter","Milk"}, {"Milk","Diapers","Cookies"}, {"Bread","Butter","Cookies"},
     {"Beer","Cookies","Diapers"}, {"Milk","Diapers","Bread","Butter"}, {"Bread","Butter","Diapers"},
     {"Beer","Diapers"}, {"Milk","Diapers","Bread","Butter"}, {"Beer","Cookies"}]
items = sorted(set().union(*T)); d = len(items)
print("Items:", items, " d =", d)

# (a) every rule X -> Y with X, Y non-empty and disjoint: R = 3^d - 2^(d+1) + 1
formula = 3**d - 2**(d + 1) + 1
brute = 0
for assign in itertools.product([0, 1, 2], repeat=d):          # 0 = not used, 1 = antecedent, 2 = consequent
    if 1 in assign and 2 in assign:
        brute += 1
print(f"\n(a) Maximum number of rules R = 3^{d} - 2^{d+1} + 1 = {formula}   (brute-force enumeration = {brute})")

# (b) with minsup > 0 an itemset is frequent iff it occurs in at least one transaction,
#     so the maximum size equals the widest transaction.
widest = max(T, key=len)
print(f"(b) Maximum frequent itemset size = size of the largest transaction = {len(widest)}  e.g. {sorted(widest)}")
for k in range(1, 6):
    n = sum(1 for c in itertools.combinations(items, k) if any(set(c) <= t for t in T))
    print(f"    itemsets of size {k} with support > 0: {n}")

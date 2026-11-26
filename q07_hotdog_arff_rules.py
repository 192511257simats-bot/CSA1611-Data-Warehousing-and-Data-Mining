"""Day 3 - Q7: Create ARFF dataset (hot dogs ...), frequent itemsets, association rules, Apriori vs FP-tree rule list.
min support = 33.33% (2 of 6 transactions), min confidence = 60%."""
import sys, os; sys.path.insert(0, "common")
from fpm_utils import *
T = [{"Hot Dogs", "Buns", "Ketchup"}, {"Hot Dogs", "Buns"}, {"Hot Dogs", "Coke", "Chips"},
     {"Chips", "Coke"}, {"Chips", "Ketchup"}, {"Hot Dogs", "Coke", "Chips"}]
T = [{i.replace(" ", "_") for i in t} for t in T]
os.makedirs("day3/output/q07", exist_ok=True)
write_transaction_arff("day3/output/q07/hotdog.arff", "hotdog_transactions", T)
print("ARFF file written: day3/output/q07/hotdog.arff\n"); print(open("day3/output/q07/hotdog.arff").read())

n = len(T); min_sup = 2; min_conf = 0.60
print(f"min_sup = 33.33% of {n} = {min_sup} transactions, min_conf = {min_conf:.0%}\n")
print("a) FREQUENT ITEMSETS (Apriori)"); fa = apriori(T, min_sup)
fp = fp_growth([sorted(t) for t in T], min_sup)
print("\nFP-Growth finds the same itemsets:", fa == fp)
rules = gen_rules(fa, n, 0.0)
print("\na) ASSOCIATION RULES"); print_rules(rules, min_conf)

print("\nb) Rules produced by APRIORI vs FP-TREE (FP-Growth) - both mine the same frequent itemsets, so the rule set is identical")
ra = {(r["A"], r["B"]) for r in gen_rules(fa, n, min_conf)}; rf = {(r["A"], r["B"]) for r in gen_rules(fp, n, min_conf)}
print("   Apriori rules:", len(ra), "| FP-Growth rules:", len(rf), "| identical:", ra == rf)
print(f"   ACCEPTED (conf >= 60%): {len(ra)}   REJECTED (conf < 60%): {len(rules) - len(ra)}")
root, *_ = build_fptree([(sorted(t), 1) for t in T], min_sup); draw_fptree(root, "day3/output/q07/fp_tree.png", "FP-Tree (min_sup = 2)")

"""Day 3 - Q5: Five transactions (M,O,N,K,E,Y ...): frequent itemsets with Apriori + FP-Growth tree.
min sup = 2 transactions, min conf = 80%.  (WEKA equivalent: load day3/output/q05/transactions.arff -> Associate -> Apriori / FPGrowth.)"""
import sys, os; sys.path.insert(0, "common")
from fpm_utils import run_full, write_transaction_arff
T = [list("MONKEY"), list("DONKEY"), list("MAKE"), list("MUCKY"), list("COOKIE")]   # T5 has 'O' twice -> a set keeps it once
os.makedirs("day3/output/q05", exist_ok=True)
write_transaction_arff("day3/output/q05/transactions.arff", "monkey", [set(t) for t in T])
run_full("Q5 database", T, min_sup=2, min_conf=0.80, outdir="day3/output/q05")

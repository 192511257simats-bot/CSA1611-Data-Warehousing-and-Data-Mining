"""Day 5 Assignment - Q1: Construct Apriori and FP-tree (support = 2, confidence = 80%) for the 10-transaction table."""
import sys, os; sys.path.insert(0, "common")
from fpm_utils import run_full
T = [list("ab"), list("bcd"), list("acde"), list("ade"), list("abc"), list("abcd"), list("a"), list("abc"), list("abd"), list("bce")]
os.makedirs("day5/output/q01", exist_ok=True)
run_full("Day 5 table 1", T, min_sup=2, min_conf=0.80, outdir="day5/output/q01")

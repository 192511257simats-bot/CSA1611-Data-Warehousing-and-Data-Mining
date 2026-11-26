"""Day 3 - Q1: Apriori and FP-Growth on the customer transaction table (support count = 3, confidence = 50%).
Each of the 10 transactions is treated as one basket."""
import sys; sys.path.insert(0, "common")
from fpm_utils import run_full

T = [list("ade"), list("abce"), list("abde"), list("acde"), list("bce"),
     list("bde"), list("cd"), list("abc"), list("ade"), list("abe")]
run_full("Customer transactions", T, min_sup=3, min_conf=0.50, outdir="day3/output/q01")

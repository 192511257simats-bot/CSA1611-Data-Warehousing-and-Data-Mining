"""Day 4 Exercise - Q6: FP-Growth rules, support = 50% (>= 3 of 5 transactions), confidence = 75%."""
import sys, os, math; sys.path.insert(0, "common")
from fpm_utils import run_full
T = [["Bread","Cheese","Egg","Juice"], ["Bread","Cheese","Juice"], ["Bread","Milk","Yogurt"], ["Bread","Juice","Milk"], ["Cheese","Juice","Milk"]]
os.makedirs("day4/exercises/output/q06", exist_ok=True)
run_full("Grocery transactions", T, min_sup=math.ceil(0.5 * len(T)), min_conf=0.75, outdir="day4/exercises/output/q06")

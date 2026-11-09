"""bench_report.py - prints the Task 8 results tables from the JSON written by bench.py"""
import json
S = [1000, 10000, 100000, 1000000]; R = {s: json.load(open(f"fc_{s}_bench.json")) for s in S}
cfg = [("oltp", "(i) OLTP"), ("star", "(ii) Star"), ("star_idx", "(iii-a) Star+IDX"), ("agg", "(iii-b) Summary")]
for qk in R[1000]["queries"]:
    print(f"\n{qk}")
    print(f"{'rows':>10} | " + " | ".join(f"{n:>26}" for _, n in cfg)); print(f"{'':>10} | " + " | ".join(f"{'time ms / scanned / VMk':>26}" for _ in cfg))
    for s in S:
        print(f"{s:>10,} | " + " | ".join(f"{R[s]['queries'][qk][k]['time_s']*1000:>8.1f} /{R[s]['queries'][qk][k]['rows_scanned']:>8,} /{R[s]['queries'][qk][k]['vm_steps_k']:>5,}" for k, _ in cfg))
print("\nExtra structures (indexes + summary table):")
print(f"{'rows':>10} | {'index build s':>13} | {'index MB':>9} | {'agg build s':>11} | {'agg rows':>9} | {'agg MB':>7} | totals identical in all 4 designs")
for s in S:
    r = R[s]; print(f"{s:>10,} | {r['index_build_s']:>13} | {r['index_mb']:>9} | {r['agg_build_s']:>11} | {r['agg_rows']:>9,} | {r['agg_mb']:>7} | {all(v['totals_match'] for v in r['queries'].values())}")
print("\nQuery plans at 1,000,000 rows, Q1:")
for k, n in cfg: print(f"  {n}:"); [print("     ", p) for p in R[1000000]['queries'][list(R[1000000]['queries'])[0]][k]['plan']]

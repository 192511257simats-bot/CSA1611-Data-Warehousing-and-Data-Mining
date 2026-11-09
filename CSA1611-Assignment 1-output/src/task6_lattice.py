"""task6_lattice.py - Task 6: enumerate the 160-cuboid lattice and pick cuboids to materialise (greedy benefit, HRU 1996).
Cuboid size estimate = min(product of level cardinalities, 1,000,000 fact rows)."""
import itertools
N = 1_000_000
LV = {"time": [("ALL", 1), ("year", 2), ("quarter", 8), ("month", 22), ("day", 669)],
      "product": [("ALL", 1), ("department", 12), ("category", 60), ("product", 50000)],
      "store": [("ALL", 1), ("state", 6), ("city", 70), ("store", 120)],
      "customer": [("ALL", 1), ("segment", 4)]}
cub = list(itertools.product(*[range(len(v)) for v in LV.values()]))
size = {c: min(N, eval("*".join(str(LV[d][i][1]) for d, i in zip(LV, c)))) for c in cub}
name = lambda c: "(" + ", ".join(LV[d][i][0] for d, i in zip(LV, c)) + ")"
print("cuboids with hierarchies:", len(cub), "| without hierarchies:", 2 ** len(LV))
base = tuple(len(v) - 1 for v in LV.values()); apex = (0, 0, 0, 0)
print("base cuboid", name(base), "rows ~", size[base], "| apex cuboid", name(apex), "rows =", size[apex])
anc = lambda a, b: all(x >= y for x, y in zip(a, b))        # b can be answered from a if a is finer-or-equal on every dimension
chosen = [base]
cost = lambda S: sum(min(size[s] for s in S if anc(s, c)) for c in cub)
print("total query cost with only base cuboid:", f"{cost(chosen):,}")
for k in range(1, 6):
    best = max((c for c in cub if c not in chosen), key=lambda c: cost(chosen) - cost(chosen + [c]))
    gain = cost(chosen) - cost(chosen + [best]); chosen.append(best)
    print(f"pick {k}: {name(best):52s} size~{size[best]:>9,}  benefit {gain:>14,}")
print("cost after 5 picks:", f"{cost(chosen):,}", f"(-{1 - cost(chosen)/cost([base]):.1%})", "| materialised fraction of lattice: 5/160 =", f"{5/160:.1%}")

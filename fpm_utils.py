"""Shared helpers: Apriori, FP-tree / FP-Growth, association rules, FP-tree drawing, ARFF writer.
Everything is written from scratch (no black box) so every step can be printed for the lab record."""
import itertools, time
from collections import Counter, defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def fmt(s):
    return "{" + ", ".join(sorted(s)) + "}"


# ---------------------------------------------------------------- Apriori
def apriori(transactions, min_sup, verbose=True):
    """min_sup = absolute support COUNT. Returns {frozenset: count} of all frequent itemsets."""
    T = [frozenset(t) for t in transactions]
    cands = [frozenset([i]) for i in sorted({i for t in T for i in t})]
    freq, k = {}, 1
    while cands:
        counts = {c: sum(1 for t in T if c <= t) for c in cands}
        Lk = {c: n for c, n in counts.items() if n >= min_sup}
        if verbose:
            print(f"\n--- C{k} (candidate {k}-itemsets with support count) ---")
            for c, n in counts.items():
                print(f"  {fmt(c):35s} {n}  {'' if n >= min_sup else '<- pruned (< min_sup)'}")
            print(f"--- L{k} (frequent {k}-itemsets) ---")
            for c, n in Lk.items():
                print(f"  {fmt(c):35s} {n}")
        freq.update(Lk)
        k += 1
        prev = sorted(tuple(sorted(c)) for c in Lk)
        nxt = set()
        for a, b in itertools.combinations(prev, 2):        # join step
            if a[:-1] == b[:-1]:
                c = frozenset(a) | frozenset(b)
                if all(frozenset(s) in Lk for s in itertools.combinations(c, k - 1)):  # prune step
                    nxt.add(c)
        cands = sorted(nxt, key=lambda c: sorted(c))
    return freq


# ---------------------------------------------------------------- FP-tree
class Node:
    def __init__(self, item, count, parent):
        self.item, self.count, self.parent, self.children = item, count, parent, {}


def _insert(root, header, items, count):
    cur = root
    for i in items:
        if i in cur.children:
            cur.children[i].count += count
        else:
            n = Node(i, count, cur)
            cur.children[i] = n
            header[i].append(n)
        cur = cur.children[i]


def build_fptree(weighted, min_sup, prefer=None):
    """weighted = list of (items, count). Returns root, header table, frequent-item counts, item order."""
    cnt = Counter()
    for items, c in weighted:
        for i in set(items):
            cnt[i] += c
    freq = {i: c for i, c in cnt.items() if c >= min_sup}
    pr = {i: r for r, i in enumerate(prefer)} if prefer else {}      # optional tie-break order (e.g. the textbook f-list)
    order = sorted(freq, key=lambda i: (-freq[i], pr.get(i, 0), i))   # descending support, ties: prefer-list, then alphabetical
    rank = {i: r for r, i in enumerate(order)}
    root, header = Node(None, 0, None), defaultdict(list)
    for items, c in weighted:
        its = sorted([i for i in set(items) if i in freq], key=rank.get)
        _insert(root, header, its, c)
    return root, header, freq, order


def fp_growth(transactions, min_sup, verbose=False, prefer=None):
    """Returns {frozenset: count}. If verbose, prints conditional pattern bases."""
    root, header, freq, order = build_fptree([(t, 1) for t in transactions], min_sup, prefer)
    out = {}

    def mine(header, order, suffix):
        for item in reversed(order):                          # least frequent first
            new = suffix | {item}
            out[frozenset(new)] = sum(n.count for n in header[item])
            base = []
            for n in header[item]:
                path, p = [], n.parent
                while p.item is not None:
                    path.append(p.item)
                    p = p.parent
                if path:
                    base.append((path[::-1], n.count))
            if verbose:
                bs = "; ".join("{" + ",".join(p) + "}:" + str(c) for p, c in base) or "-"
                print(f"  item {item:8s} cond. pattern base: {bs}")
            cnt = Counter()
            for p, c in base:
                for i in p:
                    cnt[i] += c
            cf = {i: c for i, c in cnt.items() if c >= min_sup}
            if not cf:
                continue
            croot, cheader, _, corder = build_fptree(base, min_sup)
            mine(cheader, corder, new)

    mine(header, order, frozenset())
    return out


def print_tree(root, indent=0):
    for ch in root.children.values():
        print("  " * indent + f"{ch.item}:{ch.count}")
        print_tree(ch, indent + 1)


def draw_fptree(root, path, title="FP-Tree"):
    """Draw FP-tree with matplotlib (no graphviz needed)."""
    def leaves(n):
        return 1 if not n.children else sum(leaves(c) for c in n.children.values())

    def depth(n):
        return 0 if not n.children else 1 + max(depth(c) for c in n.children.values())

    pos, edges = {}, []

    def place(n, x0, x1, d):
        pos[id(n)] = ((x0 + x1) / 2, -d, n)
        total = sum(leaves(c) for c in n.children.values()) or 1
        cur = x0
        for c in n.children.values():
            w = (x1 - x0) * leaves(c) / total
            edges.append((id(n), id(c)))
            place(c, cur, cur + w, d + 1)
            cur += w

    W = max(8, leaves(root) * 1.6)
    place(root, 0, W, 0)
    fig, ax = plt.subplots(figsize=(W, 2 + depth(root) * 1.3))
    for a, b in edges:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], "k-", lw=1, zorder=1)
    for x, y, n in pos.values():
        label = "root\n(null)" if n.item is None else f"{n.item}:{n.count}"
        ax.text(x, y, label, ha="center", va="center", fontsize=10, zorder=2,
                bbox=dict(boxstyle="round,pad=0.35", fc="#cfe8ff" if n.item else "#ffe0b2", ec="k"))
    ax.set_title(title)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=130)
    plt.close()


# ---------------------------------------------------------------- Rules
def gen_rules(freq, n, min_conf=0.0):
    """All rules A -> B from frequent itemsets. Returns list of dicts."""
    rules = []
    for iset, c in freq.items():
        if len(iset) < 2:
            continue
        for r in range(1, len(iset)):
            for A in itertools.combinations(sorted(iset), r):
                A = frozenset(A)
                B = iset - A
                conf = c / freq[A]
                if conf >= min_conf:
                    rules.append(dict(A=A, B=B, count=c, support=c / n, conf=conf,
                                      lift=conf / (freq[B] / n)))
    return sorted(rules, key=lambda r: (-r["conf"], -r["support"], sorted(r["A"])))


def print_rules(rules, min_conf=None):
    print(f"  {'Rule':45s} {'Sup':>6s} {'Conf':>7s} {'Lift':>6s}" + ("  Decision" if min_conf is not None else ""))
    for r in rules:
        s = f"  {fmt(r['A']) + ' -> ' + fmt(r['B']):45s} {r['support']:6.2f} {r['conf']:7.2%} {r['lift']:6.2f}"
        if min_conf is not None:
            s += "  ACCEPTED" if r["conf"] >= min_conf - 1e-12 else "  REJECTED"
        print(s)


def run_full(name, transactions, min_sup, min_conf, outdir, draw=True):
    """Apriori + FP-Growth + rules + FP-tree picture; returns (freq_apriori, freq_fp, rules)."""
    import os; os.makedirs(outdir, exist_ok=True)
    transactions = [sorted(set(t)) for t in transactions]
    n = len(transactions)
    print(f"{name}: {n} transactions, min_sup count = {min_sup} ({min_sup / n:.2%}), min_conf = {min_conf:.0%}")
    print("\n================ APRIORI ================")
    fa = apriori(transactions, min_sup)
    print("\n================ FP-GROWTH ================")
    root, header, freq1, order = build_fptree([(t, 1) for t in transactions], min_sup)
    print("Frequent 1-items (descending support):", ", ".join(f"{i}:{freq1[i]}" for i in order))
    print("\nFP-tree (item:count, indentation = depth):")
    print_tree(root)
    print("\nConditional pattern bases:")
    ff = fp_growth(transactions, min_sup, verbose=True)
    if draw:
        draw_fptree(root, f"{outdir}/fp_tree.png", f"FP-Tree  (min_sup = {min_sup})")
    print("\nSame result from both algorithms:", fa == ff)
    print("\nAll frequent itemsets:")
    for s, c in sorted(fa.items(), key=lambda x: (len(x[0]), sorted(x[0]))):
        print(f"  {fmt(s):35s} support count = {c}")
    rules = gen_rules(fa, n, 0.0)
    print(f"\nAssociation rules (min_conf = {min_conf:.0%}); ACCEPTED if conf >= min_conf:")
    print_rules(rules, min_conf)
    strong = [r for r in rules if r["conf"] >= min_conf - 1e-12]
    print(f"\n{len(strong)} strong rules out of {len(rules)} candidate rules")
    return fa, ff, strong


# ---------------------------------------------------------------- ARFF
def write_transaction_arff(path, relation, transactions):
    items = sorted({i for t in transactions for i in t})
    with open(path, "w") as f:
        f.write(f"@relation {relation}\n\n")
        for i in items:
            f.write(f"@attribute {i} {{t}}\n")
        f.write("\n@data\n")
        for t in transactions:
            f.write(",".join("t" if i in t else "?" for i in items) + "\n")

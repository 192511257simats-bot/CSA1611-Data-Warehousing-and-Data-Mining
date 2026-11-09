"""Shared helpers: loan data (Q1-Q3), ID3 builder, synthetic data sets."""
import math, numpy as np, pandas as pd
from sklearn.datasets import make_classification

def loan12():
    rows = [("High","Good","Salaried","Yes"),("High","Poor","Salaried","No"),
            ("High","Good","Self-employed","Yes"),("Medium","Good","Salaried","Yes"),
            ("Medium","Poor","Self-employed","No"),("Medium","Good","Self-employed","No"),
            ("Medium","Poor","Salaried","No"),("Low","Good","Salaried","Yes"),
            ("Low","Poor","Self-employed","No"),("Low","Poor","Salaried","No"),
            ("Low","Good","Self-employed","No"),("High","Poor","Self-employed","Yes")]
    df = pd.DataFrame(rows, columns=["Income","Credit","Employment","Approved"])
    df.index = range(1, 13)
    return df

def entropy(labels):
    n = len(labels)
    return -sum((c/n)*math.log2(c/n) for c in pd.Series(labels).value_counts() if c)

def gain(df, attr, cls="Approved"):
    rem = sum(len(g)/len(df)*entropy(g[cls]) for _, g in df.groupby(attr))
    return entropy(df[cls]) - rem

def id3(df, attrs, cls="Approved"):
    """Returns nested dict tree or a class label (leaf)."""
    if df[cls].nunique() == 1: return df[cls].iloc[0]
    if not attrs: return df[cls].mode()[0]
    best = max(attrs, key=lambda a: gain(df, a, cls))
    rest = [a for a in attrs if a != best]
    return {best: {v: id3(g, rest, cls) for v, g in df.groupby(best)}}

def paths(tree, prefix=()):
    if not isinstance(tree, dict): return [(prefix, tree)]
    (attr, branches), = tree.items()
    out = []
    for v, sub in branches.items(): out += paths(sub, prefix + ((attr, v),))
    return out

def credit_synth(seed=42):
    """1000 x 20, 70/30 class split, 5% label noise: stand-in for credit-g (not downloadable offline)."""
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=8, n_redundant=4,
                               weights=[0.7, 0.3], flip_y=0.05, class_sep=0.8, random_state=seed)
    return pd.DataFrame(X, columns=[f"f{i+1}" for i in range(20)]), y

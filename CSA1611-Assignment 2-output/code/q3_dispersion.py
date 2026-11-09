"""Q3 - Data dispersion: delivery times (24 orders). Verification of manual calculations."""
import numpy as np, statistics as st
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

data = [28,31,33,35,35,36,38,40,41,42,42,43,45,46,48,50,52,53,55,58,61,64,72,95]

def quart_median_of_halves(x):
    x = sorted(x); n = len(x); h = n // 2
    return st.median(x[:h]), st.median(x), st.median(x[h + (n % 2):])

def measures(x, label):
    x = sorted(x); n = len(x)
    mean = sum(x)/n; med = st.median(x)
    mode = st.multimode(x); mid = (x[0]+x[-1])/2
    q1, q2, q3 = quart_median_of_halves(x); iqr = q3-q1
    var_s = np.var(x, ddof=1); var_p = np.var(x)
    lo, hi = q1-1.5*iqr, q3+1.5*iqr
    out = [v for v in x if v < lo or v > hi]
    print(f"--- {label} (n={n}) ---")
    print(f"sum={sum(x)} mean={mean:.4f} median={med} mode={mode} midrange={mid}")
    print(f"range={x[-1]-x[0]} Q1={q1} Q2={q2} Q3={q3} IQR={iqr}")
    print(f"sample variance={var_s:.4f} sample SD={var_s**.5:.4f} | population variance={var_p:.4f} SD={var_p**.5:.4f}")
    print(f"five-number summary: {x[0]}, {q1}, {q2}, {q3}, {x[-1]}")
    print(f"1.5*IQR fences: [{lo}, {hi}]  outliers: {out}")
    print(f"skewness={stats.skew(x):.4f}")
    return dict(mean=mean, median=med, mid=mid, rng=x[-1]-x[0], q1=q1, q3=q3, iqr=iqr, var=var_s, sd=var_s**.5)

a = measures(data, "ORIGINAL")
b = measures(data[:-1], "AFTER REMOVING 95")
print("\nPercentage change after removing 95:")
for k in a: print(f"  {k:7s}: {a[k]:9.3f} -> {b[k]:9.3f}  ({(b[k]-a[k])/a[k]*100:+.1f}%)")
print("\nPandas/NumPy check -> numpy percentile (linear) Q1,Q3:", np.percentile(data,[25,75]))

fig, ax = plt.subplots(figsize=(8,3))
ax.boxplot(data, orientation="horizontal", whis=1.5, patch_artist=True, boxprops=dict(facecolor="#9ecae1"))
ax.set_xlabel("Delivery time (minutes)"); ax.set_yticks([]); ax.set_title("Boxplot of delivery times (whiskers = 1.5 x IQR)")
ax.annotate("outlier 95", (95,1), xytext=(80,1.25), arrowprops=dict(arrowstyle="->"))
plt.tight_layout(); plt.savefig("../out/q3_boxplot.png", dpi=200)

"""Q4 - Binning (equal-frequency, depth 4), smoothing by means and boundaries; imputation effect on dispersion."""
import numpy as np
vals = [5,9,11,14,18,19,23,26,27,30,33,38]
depth = 4
bins = [vals[i:i+depth] for i in range(0, len(vals), depth)]
print("Equal-frequency bins (depth 4):")
for i,b in enumerate(bins,1): print(f" Bin{i}: {b}")
print("\nSmoothing by bin means:")
for i,b in enumerate(bins,1): print(f" Bin{i}: mean={np.mean(b):.2f} -> {[round(float(np.mean(b)),2)]*len(b)}")
print("\nSmoothing by bin boundaries:")
for i,b in enumerate(bins,1):
    lo,hi=b[0],b[-1]; sm=[lo if (v-lo)<=(hi-v) else hi for v in b]
    print(f" Bin{i}: {b} -> {sm}")

print("\nEffect of global-mean imputation on dispersion (simulation):")
rng = np.random.default_rng(1)
x = rng.normal(20, 8, 1000); mask = rng.random(1000) < 0.3
obs = x.copy(); obs[mask] = np.nan
mean_obs = np.nanmean(obs); imp = np.where(np.isnan(obs), mean_obs, obs)
print(f" True SD={x.std(ddof=1):.3f}  | SD of observed={np.nanstd(obs,ddof=1):.3f} | SD after mean imputation (30% missing)={imp.std(ddof=1):.3f}")
print(f" Variance shrinkage factor = {imp.var(ddof=1)/np.nanvar(obs,ddof=1):.3f} (expected ~ 0.70)")

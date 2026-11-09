"""Q5 - Pearson correlation, chi-square, normalisation, Euclidean distance."""
import numpy as np
from scipy import stats
att = np.array([60,70,75,80,85,90]); mk = np.array([52,58,66,70,79,85])
r = np.corrcoef(att, mk)[0,1]
print("PEARSON: mean(att)=%.4f mean(marks)=%.4f"%(att.mean(), mk.mean()))
da, dm = att-att.mean(), mk-mk.mean()
print(" sum(da*dm)=%.4f sum(da^2)=%.4f sum(dm^2)=%.4f"%((da*dm).sum(), (da**2).sum(), (dm**2).sum()))
print(" r = %.4f  (scipy: %.4f)"%(r, stats.pearsonr(att,mk)[0]))

obs = np.array([[120,180],[80,320]])
row, col, n = obs.sum(1), obs.sum(0), obs.sum()
exp = np.outer(row, col)/n
chi = ((obs-exp)**2/exp).sum()
print("\nCHI-SQUARE expected values:\n", np.round(exp,2))
print(" cell contributions:\n", np.round((obs-exp)**2/exp,3))
print(" chi2 = %.3f (df=1, critical=3.84) -> %s"%(chi, "reject independence" if chi>3.84 else "independent"))
c2, p, dof, _ = stats.chi2_contingency(obs, correction=False)
print(" scipy chi2=%.3f p=%.2e dof=%d"%(c2,p,dof))

inc = np.array([20000,35000,50000,80000,150000], float)
mm = (inc-inc.min())/(inc.max()-inc.min())
mu, sd_p, sd_s = inc.mean(), inc.std(), inc.std(ddof=1)
print("\nNORMALISATION of income", inc)
print(" min-max :", np.round(mm,4))
print(" mean=%.0f  population SD=%.2f  sample SD=%.2f"%(mu,sd_p,sd_s))
print(" z-score (population SD):", np.round((inc-mu)/sd_p,4))
print(" z-score (sample SD)    :", np.round((inc-mu)/sd_s,4))
j = len(str(int(abs(inc).max())))
print(" decimal scaling j=%d :"%j, inc/10**j)

a, b = np.array([19,35000.]), np.array([21,80000.])
print("\nEUCLIDEAN distance raw = %.4f"%np.linalg.norm(a-b))
lo, hi = np.array([17,20000.]), np.array([25,150000.])
na, nb = (a-lo)/(hi-lo), (b-lo)/(hi-lo)
print(" normalised A=",np.round(na,4)," B=",np.round(nb,4))
print(" diffs: age=%.4f income=%.4f ; distance after min-max = %.4f"%(abs(na[0]-nb[0]),abs(na[1]-nb[1]),np.linalg.norm(na-nb)))
print(" share of squared distance due to income BEFORE = %.5f%%"%(100*(45000**2)/(45000**2+4)))

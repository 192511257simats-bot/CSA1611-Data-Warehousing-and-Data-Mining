"""Q5 - SVM geometry, kernels, C, gamma and scaling."""
import numpy as np, pandas as pd, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_circles, load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import make_pipeline
warnings.filterwarnings("ignore")
P = np.array([[3,3],[4,3],[4,4],[1,1],[1,2],[2,1]], float); y = np.array([1,1,1,-1,-1,-1])
print("=== Student A: geometry (hard margin via C=1e6) ===")
m = SVC(kernel="linear", C=1e6).fit(P, y); w = m.coef_[0]; b = m.intercept_[0]
print("support vectors:", m.support_vectors_.tolist()); print("w = %s  b = %.4f   -> %.3f x1 + %.3f x2 %+.3f = 0" % (np.round(w,4), b, w[0], w[1], b))
print("margin width 2/||w|| = %.4f   (analytic 3/sqrt2 = %.4f)" % (2/np.linalg.norm(w), 3/np.sqrt(2)))
print("Check by hand: w=(2/3,2/3), b=-3 -> f(3,3)=+1, f(1,2)=f(2,1)=-1:",
      [round(float(np.dot([2/3,2/3], p)-3), 3) for p in ([3,3],[1,2],[2,1])])
for name, keep in (("remove non-support point (4,4)", [0,1,3,4,5]), ("remove non-support point (1,1)", [0,1,2,4,5]), ("remove support vector (3,3)", [1,2,3,4,5])):
    mm = SVC(kernel="linear", C=1e6).fit(P[keep], y[keep]); ww = mm.coef_[0]
    print(f"{name:<34}: w={np.round(ww,3)} b={mm.intercept_[0]:.3f} margin={2/np.linalg.norm(ww):.3f} SVs={mm.support_vectors_.tolist()}")
xs = np.linspace(0, 5.5, 50); plt.figure(figsize=(5, 4.4))
plt.scatter(*P[y==1].T, c="tab:blue", s=70, label="class +1"); plt.scatter(*P[y==-1].T, c="tab:red", s=70, label="class -1")
plt.scatter(*m.support_vectors_.T, s=260, facecolors="none", edgecolors="k", lw=1.6, label="support vectors")
for off, st in ((0, "-"), (1, "--"), (-1, "--")): plt.plot(xs, (-b + off - w[0]*xs)/w[1], "k"+st, lw=1.2)
plt.xlim(0, 5.5); plt.ylim(0, 5.5); plt.legend(loc="upper right", fontsize=8); plt.title("Max-margin hyperplane x1 + x2 = 4.5 (margin 2.12)"); plt.grid(alpha=.3)
plt.savefig("figs/q5_margin.png", dpi=150, bbox_inches="tight"); plt.close()

print("\n=== Student B: concentric circles (n=400, noise 0.12), 70/30 split ===")
X, yc = make_circles(400, noise=0.12, factor=0.45, random_state=1); Xtr, Xte, ytr, yte = train_test_split(X, yc, test_size=.3, random_state=1, stratify=yc)
print(f"{'kernel':<22} {'C':>6} {'train':>7} {'test':>7} {'#SV':>5}")
fig, ax = plt.subplots(1, 3, figsize=(11, 3.4)); g = np.mgrid[-1.6:1.6:200j, -1.6:1.6:200j]
for a, (nm, kw) in zip(ax, (("linear", dict(kernel="linear")), ("poly deg 3", dict(kernel="poly", degree=3, gamma="scale")), ("RBF", dict(kernel="rbf", gamma=1)))):
    mk = SVC(C=1, **kw).fit(Xtr, ytr); print(f"{nm:<22} {1:>6} {mk.score(Xtr,ytr):>7.3f} {mk.score(Xte,yte):>7.3f} {mk.n_support_.sum():>5}")
    a.contourf(g[0], g[1], mk.predict(np.c_[g[0].ravel(), g[1].ravel()]).reshape(g[0].shape), alpha=.25, cmap="coolwarm"); a.scatter(*Xte.T, c=yte, s=10, cmap="coolwarm"); a.set_title(f"{nm}  test acc {mk.score(Xte,yte):.2f}", fontsize=9)
plt.tight_layout(); plt.savefig("figs/q5_kernels.png", dpi=150); plt.close()
print("\nEffect of C (RBF, gamma=1):")
for C in (0.01, 0.1, 1, 10, 100, 1000):
    mk = SVC(C=C, kernel="rbf", gamma=1).fit(Xtr, ytr); print(f"{'rbf g=1':<22} {C:>6} {mk.score(Xtr,ytr):>7.3f} {mk.score(Xte,yte):>7.3f} {mk.n_support_.sum():>5}")
print("\nEffect of gamma (RBF, C=1):")
for gm in (0.01, 0.1, 1, 10, 100, 1000):
    mk = SVC(C=1, kernel="rbf", gamma=gm).fit(Xtr, ytr); print(f"{'rbf gamma='+str(gm):<22} {1:>6} {mk.score(Xtr,ytr):>7.3f} {mk.score(Xte,yte):>7.3f} {mk.n_support_.sum():>5}")
print("\nEffect of NOT scaling (RBF, C=1, gamma='scale', 5-fold CV mean accuracy)")
bc = load_breast_cancer()
raw = cross_val_score(SVC(), bc.data, bc.target, cv=5).mean(); scl = cross_val_score(make_pipeline(StandardScaler(), SVC()), bc.data, bc.target, cv=5).mean()
print(f"  Breast cancer (feature ranges 0.01 .. 4000): unscaled {raw:.3f}  scaled {scl:.3f}")
Xbad = Xtr.copy(); Xbad[:, 1] *= 1000; Xbadt = Xte.copy(); Xbadt[:, 1] *= 1000
mu = SVC(kernel="rbf", gamma="scale").fit(Xbad, ytr); sc = StandardScaler().fit(Xbad); ms = SVC(kernel="rbf", gamma="scale").fit(sc.transform(Xbad), ytr)
print(f"  Circles with x2 multiplied by 1000: unscaled test {mu.score(Xbadt,yte):.3f} (#SV {mu.n_support_.sum()})  scaled test {ms.score(sc.transform(Xbadt),yte):.3f} (#SV {ms.n_support_.sum()})")

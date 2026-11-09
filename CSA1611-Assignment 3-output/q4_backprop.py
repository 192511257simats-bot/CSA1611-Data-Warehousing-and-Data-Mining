"""Q4 - Backpropagation: hand-calculation reproduced in code + MLP experiments."""
import time, numpy as np, pandas as pd, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier
from common import credit_synth
warnings.filterwarnings("ignore")
sig = lambda z: 1/(1+np.exp(-z))
x = np.array([1., 0.]); t = 1.; lr = 0.9
W1 = np.array([[0.2, -0.3], [0.4, 0.1]])       # rows: x1,x2 ; cols: h1,h2
b1 = np.array([-0.4, 0.2]); W2 = np.array([-0.3, -0.2]); b2 = 0.1
def forward(W1, b1, W2, b2):
    zh = x @ W1 + b1; h = sig(zh); zo = h @ W2 + b2; return zh, h, zo, sig(zo)
print("=== Student A: one training step (sigmoid, lr=0.9) ===")
zh, h, zo, o = forward(W1, b1, W2, b2)
print("net_h1 = %.4f -> h1 = %.4f" % (zh[0], h[0])); print("net_h2 = %.4f -> h2 = %.4f" % (zh[1], h[1]))
print("net_o  = %.4f -> o  = %.4f   (target 1)  error 0.5(t-o)^2 = %.5f" % (zo, o, 0.5*(t-o)**2))
d_o = o*(1-o)*(t-o); d_h = h*(1-h)*d_o*W2
print("delta_o  = o(1-o)(t-o)        = %.5f" % d_o)
print("delta_h1 = h1(1-h1)*delta_o*w = %.5f" % d_h[0]); print("delta_h2 = h2(1-h2)*delta_o*w = %.5f" % d_h[1])
W2n = W2 + lr*d_o*h; b2n = b2 + lr*d_o; W1n = W1 + lr*np.outer(x, d_h); b1n = b1 + lr*d_h
print("\nUpdated weights/biases:")
print("  w(h1->o): %.4f -> %.4f   w(h2->o): %.4f -> %.4f   bias_o: %.4f -> %.4f" % (W2[0], W2n[0], W2[1], W2n[1], b2, b2n))
print("  w(x1->h1): %.4f -> %.4f  w(x2->h1): %.4f -> %.4f  bias_h1: %.4f -> %.4f" % (W1[0,0], W1n[0,0], W1[1,0], W1n[1,0], b1[0], b1n[0]))
print("  w(x1->h2): %.4f -> %.4f  w(x2->h2): %.4f -> %.4f  bias_h2: %.4f -> %.4f" % (W1[0,1], W1n[0,1], W1[1,1], W1n[1,1], b1[1], b1n[1]))
_, h2, _, o2 = forward(W1n, b1n, W2n, b2n)
print("\nAfter update: h1=%.4f h2=%.4f o=%.4f error=%.5f  (before %.5f)  -> error decreased: %s" %
      (h2[0], h2[1], o2, 0.5*(t-o2)**2, 0.5*(t-o)**2, 0.5*(t-o2)**2 < 0.5*(t-o)**2))
print("\nSymmetry demo: all weights = 0.5, biases = 0 -> after 50 steps do h1, h2 differ?")
Wa = np.full((2, 2), .5); ba = np.zeros(2); Wb = np.full(2, .5); bb = 0.
for _ in range(50):
    zh = x@Wa+ba; hh = sig(zh); oo = sig(hh@Wb+bb); do = oo*(1-oo)*(t-oo); dh = hh*(1-hh)*do*Wb
    Wb = Wb+lr*do*hh; bb += lr*do; Wa = Wa+lr*np.outer(x, dh); ba = ba+lr*dh
print("  h1=%.6f h2=%.6f  w(h1->o)=%.6f w(h2->o)=%.6f  (identical -> hidden units never specialise)" % (hh[0], hh[1], Wb[0], Wb[1]))

print("\n=== Student B: MLP behaviour on a REAL data set (breast cancer 569x30, scaled, 70/30 split) ===")
bc = load_breast_cancer(); Xtr, Xte, ytr, yte = train_test_split(bc.data, bc.target, test_size=.3, stratify=bc.target, random_state=1)
sc = StandardScaler().fit(Xtr); Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
print(f"{'lr':>6} {'hidden':>7} {'epochs':>7} {'train':>7} {'test':>7} {'sec':>7}")
for lr_ in (0.001, 0.01, 0.1, 1.0):
    for hid in (2, 10, 50):
        for ep in (10, 100, 500):
            m = MLPClassifier((hid,), solver="sgd", learning_rate_init=lr_, max_iter=ep, momentum=0.9, random_state=1)
            t0 = time.time(); m.fit(Xtr, ytr); s = time.time()-t0
            if hid == 10 or (lr_ == 0.01 and hid in (2, 50)):
                print(f"{lr_:>6} {hid:>7} {ep:>7} {m.score(Xtr,ytr):>7.3f} {m.score(Xte,yte):>7.3f} {s:>7.3f}")
print("\n=== Overfitting / instability on a noisy data set (credit_synth, 5% label noise) ===")
X, y = credit_synth(); Xa, Xb, ya, yb = train_test_split(X, y, test_size=.3, stratify=y, random_state=1)
sc2 = StandardScaler().fit(Xa); Xa, Xb = sc2.transform(Xa), sc2.transform(Xb)
curves = {}
for name, hid, lr_ in (("10 hidden, lr 0.01", 10, .01), ("200 hidden, lr 0.05", 200, .05), ("10 hidden, lr 3.0 (too big)", 10, 3.0)):
    m = MLPClassifier((hid,), solver="sgd", learning_rate_init=lr_, momentum=0.9, random_state=1); tr, te = [], []
    for ep in range(300):
        m.partial_fit(Xa, ya, classes=[0, 1]); tr.append(m.score(Xa, ya)); te.append(m.score(Xb, yb))
    curves[name] = (tr, te)
    print(f"{name:<28} epoch 20: train {tr[19]:.3f} test {te[19]:.3f} | epoch 300: train {tr[-1]:.3f} test {te[-1]:.3f} | best test {max(te):.3f} @ epoch {int(np.argmax(te))+1}")
fig, ax = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
for a, (n, (tr, te)) in zip(ax, curves.items()):
    a.plot(tr, label="train"); a.plot(te, label="test"); a.set_title(n, fontsize=9); a.set_xlabel("epoch"); a.grid(alpha=.3)
ax[0].set_ylabel("accuracy"); ax[0].legend(); plt.tight_layout(); plt.savefig("figs/q4_curves.png", dpi=150); plt.close()
t0 = time.time(); MLPClassifier((50,), max_iter=500, random_state=1).fit(Xa, ya); tm = time.time()-t0
t0 = time.time(); dt = DecisionTreeClassifier(criterion="entropy", random_state=1).fit(Xa, ya); td = time.time()-t0
print(f"\nTraining time (credit_synth): MLP(50 hidden, adam, 500 it) {tm:.3f}s  vs  decision tree {td:.4f}s  ({tm/td:.0f}x)")

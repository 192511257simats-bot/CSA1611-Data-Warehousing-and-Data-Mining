"""Q6 - Discretization: equal-width, equal-frequency, entropy-based split."""
import numpy as np
from math import log2
t = [3,7,7,9,12,14,14,15,18,21,21,22,25,25,27,31,36,36,40,44]
k=4; lo,hi=min(t),max(t); w=(hi-lo)/k
edges=[lo+i*w for i in range(k+1)]
print("EQUAL-WIDTH: width=(%d-%d)/4=%.2f"%(hi,lo,w))
for i in range(k):
    a,b=edges[i],edges[i+1]
    m=[v for v in t if (a<=v<b or (i==k-1 and v==b))]
    print(f" [{a:.2f}, {b:.2f}{']' if i==k-1 else ')'} -> {len(m)} values {m}")
print("\nEQUAL-FREQUENCY (5 per bin):")
for i in range(k): print(f" Bin{i+1}: {t[i*5:(i+1)*5]}")

vals=[10,12,15,18,22,25,28,31,35,40]; cls="NNNNYYNYYY"
def H(lbls):
    n=len(lbls); 
    return -sum((lbls.count(c)/n)*log2(lbls.count(c)/n) for c in set(lbls)) if n else 0
H0=H(list(cls)); print("\nENTROPY-BASED SPLIT: H(S)=%.4f"%H0)
best=None; print(f"{'split':>7} {'left(N,Y)':>10} {'right(N,Y)':>11} {'H_left':>7} {'H_right':>8} {'E(S,T)':>7} {'Gain':>7}")
for i in range(len(vals)-1):
    s=(vals[i]+vals[i+1])/2; L=list(cls[:i+1]); R=list(cls[i+1:])
    E=len(L)/10*H(L)+len(R)/10*H(R); g=H0-E
    print(f"{s:7.1f} {str((L.count('N'),L.count('Y'))):>10} {str((R.count('N'),R.count('Y'))):>11} {H(L):7.4f} {H(R):8.4f} {E:7.4f} {g:7.4f}")
    if best is None or g>best[1]: best=(s,g)
print("BEST split = %.1f with gain %.4f"%best)

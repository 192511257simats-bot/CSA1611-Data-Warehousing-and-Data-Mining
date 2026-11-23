"""TASK 6 - Spatial clustering of incident locations: k-means vs DBSCAN, k-distance graph, effect of eps.
Data: SYNTHETIC GPS incidents around Chennai (13.0827N, 80.2707E), generated with numpy seed 7 (documented in report)."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import adjusted_rand_score
rng=np.random.default_rng(7); LAT0,LON0=13.0827,80.2707
def make_points():
    P=[];L=[]
    a=rng.normal([0,0],0.35,(380,2)); P.append(a); L+= [0]*380                      # hot-spot 1: round junction cluster
    t=rng.uniform(0,np.pi,420); c=np.c_[4+2.2*np.cos(t),1.0+2.2*np.sin(t)]+rng.normal(0,.12,(420,2)); P.append(c); L+=[1]*420   # hot-spot 2: crescent (flyover curve)
    s=rng.uniform(-3,3,400); r=np.c_[-3+s*.9+0, -4+ s*0.45]+rng.normal(0,.10,(400,2)); P.append(r); L+=[2]*400                 # hot-spot 3: elongated arterial-road corridor
    n=np.c_[rng.uniform(-5,8,200),rng.uniform(-6,6,200)]; P.append(n); L+=[-1]*200                                          # scattered noise
    return np.vstack(P),np.array(L)
XY,true=make_points()            # coordinates in km from the city centre
lat=LAT0+XY[:,1]/111.0; lon=LON0+XY[:,0]/(111.32*np.cos(np.radians(LAT0)))
pd.DataFrame({"lat":lat.round(6),"lon":lon.round(6),"x_km":XY[:,0].round(4),"y_km":XY[:,1].round(4),"true_label":true}).to_csv("../outputs/incidents.csv",index=False)
print(f"Incidents generated: {len(XY)} points (3 hot-spots of different shapes + {np.sum(true==-1)} noise). Saved incidents.csv")
print(f"lat range {lat.min():.4f}-{lat.max():.4f}, lon range {lon.min():.4f}-{lon.max():.4f}")
# ---------- k-means ----------
km=KMeans(4,n_init=10,random_state=7).fit(XY)
print("\nk-means (k=4): cluster sizes",np.bincount(km.labels_),"| ARI vs truth = %.3f | noise points identified = 0 (k-means assigns every point)"%adjusted_rand_score(true,km.labels_))
# ---------- k-distance graph ----------
MINPTS=10
d,_=NearestNeighbors(n_neighbors=MINPTS).fit(XY).kneighbors(XY); kd=np.sort(d[:,-1])
# knee = point of maximum distance from the chord joining first & last points
x=np.arange(len(kd)); p1=np.array([0,kd[0]]); p2=np.array([len(kd)-1,kd[-1]])
v=p2-p1; w=np.c_[x,kd]-p1; dist=np.abs(v[0]*w[:,1]-v[1]*w[:,0])/np.linalg.norm(v); kn=int(dist.argmax()); EPS=float(kd[kn])
print(f"\nk-distance (k=MinPts={MINPTS}): knee at rank {kn}, eps ~ {EPS:.3f} km (~{EPS*1000:.0f} m)")
fig,ax=plt.subplots(figsize=(6,3.6)); ax.plot(kd,color="#1f4e79"); ax.axhline(EPS,color="#c0392b",ls="--",label=f"chosen eps = {EPS:.2f} km"); ax.scatter([kn],[EPS],color="#c0392b",zorder=3)
ax.set_xlabel("points sorted by distance"); ax.set_ylabel(f"distance to {MINPTS}th neighbour (km)"); ax.set_title("k-distance graph"); ax.legend(); fig.tight_layout(); fig.savefig("../figs/fig_kdist.png",dpi=200); plt.close()
# ---------- DBSCAN + effect of eps ----------
print("\n eps(km) | clusters | noise pts | ARI vs ground truth")
fig,axs=plt.subplots(1,4,figsize=(15,3.8)); cols=["#1f77b4","#2ca02c","#ff7f0e","#9467bd","#8c564b","#17becf","#e377c2","#bcbd22"]
for ax,f in zip(axs,[0.4,1.0,2.0,6.0]):
    e=EPS*f; lb=DBSCAN(eps=e,min_samples=MINPTS).fit(XY).labels_; nc=len(set(lb)-{-1}); nn=(lb==-1).sum()
    print(f" {e:6.3f}  |   {nc:3d}    |   {nn:4d}    | {adjusted_rand_score(true,lb):.3f}   {'<- chosen' if f==1.0 else ''}")
    for k in set(lb):
        m=lb==k; ax.scatter(XY[m,0],XY[m,1],s=5,c="lightgrey" if k==-1 else cols[k%8],marker="x" if k==-1 else "o")
    ax.set_title(f"eps={e:.2f} km: {nc} clusters, {nn} noise"); ax.set_aspect("equal")
fig.tight_layout(); fig.savefig("../figs/fig_eps_effect.png",dpi=200); plt.close()
lb=DBSCAN(eps=EPS,min_samples=MINPTS).fit(XY).labels_; print("\nChosen DBSCAN: clusters =",len(set(lb)-{-1}),"sizes =",[int((lb==k).sum()) for k in sorted(set(lb)-{-1})],"noise =",int((lb==-1).sum()),
      "| true noise points labelled noise: %d/200"%int(((lb==-1)&(true==-1)).sum()))
# ---------- comparison plot ----------
fig,axs=plt.subplots(1,3,figsize=(15,4.2))
axs[0].scatter(XY[:,0],XY[:,1],s=5,c=np.where(true==-1,"lightgrey",np.array(cols)[np.clip(true,0,7)]) ); axs[0].set_title("Ground truth (grey = noise)")
for k in range(4): m=km.labels_==k; axs[1].scatter(XY[m,0],XY[m,1],s=5,c=cols[k])
axs[1].scatter(*km.cluster_centers_.T,c="k",marker="*",s=140); axs[1].set_title("k-means (k=4): no noise, shapes cut")
for k in set(lb):
    m=lb==k; axs[2].scatter(XY[m,0],XY[m,1],s=5,c="lightgrey" if k==-1 else cols[k%8],marker="x" if k==-1 else "o")
axs[2].set_title(f"DBSCAN (eps={EPS:.2f} km, MinPts={MINPTS}): noise in grey x")
for a in axs: a.set_aspect("equal"); a.set_xlabel("x (km)")
fig.tight_layout(); fig.savefig("../figs/fig_kmeans_vs_dbscan.png",dpi=200); plt.close()
np.save("../outputs/dbscan_labels.npy",lb); open("../outputs/eps.txt","w").write(str(EPS))

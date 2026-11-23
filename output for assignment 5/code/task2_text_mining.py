"""TASK 2 - Text mining: vectorise, 4 feature settings, NB + linear SVM, k-means vs labels, error analysis."""
import numpy as np, warnings; warnings.filterwarnings("ignore")
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, adjusted_rand_score, normalized_mutual_info_score
from sklearn.cluster import KMeans
from corpus import make_corpus, analyzer, CATS
SEED=42
docs, y, names = make_corpus(120, SEED); y=np.array(y)
print(f"Corpus: {len(docs)} synthetic complaints, {len(names)} classes {names}, seed={SEED}")
print("Sample:", docs[0], "|", y[0])
Xtr,Xte,ytr,yte,itr,ite = train_test_split(docs,y,np.arange(len(docs)),test_size=0.3,stratify=y,random_state=SEED)
settings = {
 "F1 binary, no stop, no stem, all vocab": lambda: CountVectorizer(analyzer=analyzer(False,False), binary=True),
 "F2 TF-IDF, stop-words removed, no stem": lambda: TfidfVectorizer(analyzer=analyzer(True,False)),
 "F3 TF-IDF, stop removed + stemming":     lambda: TfidfVectorizer(analyzer=analyzer(True,True)),
 "F4 as F3 but vocabulary limited to 40":  lambda: TfidfVectorizer(analyzer=analyzer(True,True), max_features=40),
}
clfs = {"NaiveBayes": lambda: MultinomialNB(), "LinearSVM": lambda: LinearSVC(random_state=SEED)}
print("\n=== Feature-setting comparison (70/30 stratified split; 5-fold CV on train in brackets) ===")
print(f"{'Setting':45s}{'|V|':>5s}  {'NaiveBayes':>18s}  {'LinearSVM':>18s}")
res={}
for sn,mk in settings.items():
    v=mk().fit(Xtr); row=f"{sn:45s}{len(v.vocabulary_):5d}"
    for cn,mc in clfs.items():
        p=make_pipeline(mk(),mc()); p.fit(Xtr,ytr); acc=accuracy_score(yte,p.predict(Xte))
        cv=cross_val_score(make_pipeline(mk(),mc()),Xtr,ytr,cv=5).mean(); res[(sn,cn)]=acc
        row+=f"  {acc:7.3f} ({cv:6.3f})"
    print(row)
best_s="F3 TF-IDF, stop removed + stemming"
for cn,mc in clfs.items():
    p=make_pipeline(settings[best_s](),mc()).fit(Xtr,ytr); pr=p.predict(Xte)
    print(f"\n=== {cn} with {best_s} : accuracy = {accuracy_score(yte,pr):.3f} ===")
    cm=confusion_matrix(yte,pr,labels=names)
    print("Confusion matrix (rows=true, cols=predicted):", names)
    print(cm)
    print(classification_report(yte,pr,labels=names,digits=3))
    if cn=="LinearSVM":
        wrong=np.where(pr!=yte)[0]; print(f"--- Misclassified test documents ({len(wrong)}) ---")
        for i in wrong[:12]:
            t=Xte[i]; toks=set(analyzer(False,False)(t))
            hits={c:sorted(toks & set(w for w in CATS[c])) for c in names}
            hits={c:h for c,h in hits.items() if h}
            print(f"true={yte[i]:11s} pred={pr[i]:11s} | {t}\n      category-words present: {hits}")
# ---- k-means on unlabelled documents ----
v=settings[best_s](); X=v.fit_transform(docs)
km=KMeans(n_clusters=5,n_init=10,random_state=SEED).fit(X)
print("\n=== k-means (k=5) on TF-IDF (labels ignored while clustering) ===")
import pandas as pd
ct=pd.crosstab(pd.Series(km.labels_,name="cluster"),pd.Series(y,name="true category")); print(ct)
pur=ct.max(axis=1).sum()/len(y)
print(f"Purity={pur:.3f}  ARI={adjusted_rand_score(y,km.labels_):.3f}  NMI={normalized_mutual_info_score(y,km.labels_):.3f}")
terms=np.array(v.get_feature_names_out())
for k in range(5): print(f"cluster {k} top terms:", list(terms[km.cluster_centers_[k].argsort()[::-1][:5]]))

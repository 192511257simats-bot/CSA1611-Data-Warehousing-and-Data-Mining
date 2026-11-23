"""Synthetic Metro City complaint corpus (documented, reproducible; seed fixed).
5 categories x 120 complaints = 600 documents. ~12% of complaints contain one
'distractor' word from another category and ~6% are genuinely mixed-topic."""
import random
CATS = {
 "Roads":       ["pothole","road","crack","tar","footpath","bridge","traffic","signal","speed breaker","diversion"],
 "Water":       ["water","leak","pipeline","tap","supply","tank","borewell","drinking","pressure","valve"],
 "Sanitation":  ["garbage","drain","sewage","waste","dustbin","sweeping","stench","overflow","dumping","toilet"],
 "Electricity": ["power","light","electric","transformer","wire","pole","voltage","outage","meter","streetlight"],
 "Health":      ["hospital","fever","mosquito","clinic","dengue","ambulance","doctor","medicine","fogging","vaccine"],
}
VERB = {"leak":["leak","leaks","leaking","leaked"],"crack":["crack","cracks","cracked"],
        "overflow":["overflow","overflowing","overflows"],"dump":["dumping","dumped"]}
GENERIC = ["near school","main road area","for many days","in our ward","near market","on the street","since last week",
           "please act urgently","residents are suffering","at the junction","behind the temple","near bus stop"]
FILL = ["the","is","not","in","for","has","are","a","of","and"]
def make_corpus(per_class=120, seed=42):
    rnd = random.Random(seed); docs=[]; labels=[]; names=list(CATS)
    for c in names:
        for _ in range(per_class):
            w = rnd.sample(CATS[c], rnd.choice([2,3]))
            r = rnd.random()
            if r < 0.12:               # distractor word from another class
                o = rnd.choice([x for x in names if x!=c]); w.append(rnd.choice(CATS[o]))
            elif r < 0.18:             # truly mixed complaint (two topics)
                o = rnd.choice([x for x in names if x!=c]); w += rnd.sample(CATS[o],2)
            w = [rnd.choice(VERB[x]) if x in VERB and rnd.random()<.7 else x for x in w]
            toks = w + rnd.choice(GENERIC).split() + rnd.sample(FILL, 3)
            rnd.shuffle(toks); docs.append(" ".join(toks)); labels.append(c)
    idx=list(range(len(docs))); rnd.shuffle(idx)
    return [docs[i] for i in idx],[labels[i] for i in idx],names
STOP = set("the is not in for has are a of and on at to near our since many".split())
def stem(w):
    for s in ("ing","ed","es","s"):
        if w.endswith(s) and len(w)-len(s)>=3: return w[:-len(s)]
    return w
def analyzer(stop=False, stemming=False):
    def f(t):
        toks=t.lower().split()
        if stop: toks=[x for x in toks if x not in STOP]
        if stemming: toks=[stem(x) for x in toks]
        return toks
    return f

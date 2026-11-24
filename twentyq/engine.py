import math
from .questions import QUESTIONS

LIKES = {
 "yes":(0.96,0.04), "probably yes":(0.82,0.18),
 "sometimes":(0.58,0.58), "probably no":(0.18,0.82), "no":(0.04,0.96)
}
def normalize_response(s):
    v=str(s or "").strip().casefold()
    return {"y":"yes","n":"no","u":"unknown","yeah":"yes","nope":"no",
      "maybe":"sometimes","occasionally":"sometimes","not sure":"unknown",
      "don't know":"unknown","dont know":"unknown","definitely yes":"yes",
      "definitely no":"no","likely yes":"probably yes","likely no":"probably no"}.get(v,v)

class Engine:
    def __init__(self, concepts):
        self.concepts=concepts
        self.weights={c["word"]:max(.01,c.get("confidence",.8)) for c in concepts}
        self.asked=set(); self.history=[]
    def answer(self,key,response):
        if response=="unknown":
            self.asked.add(key); self.history.append((key,response)); return
        yes,no=LIKES[response]
        for c in self.concepts:
            v=c["attributes"].get(key)
            factor=.72 if v is None else (yes if v else no)
            self.weights[c["word"]]*=factor
        total=sum(self.weights.values())
        if total:
            self.weights={k:v/total for k,v in self.weights.items()}
        self.asked.add(key); self.history.append((key,response))
    def ranked(self):
        return sorted(self.concepts,key=lambda c:self.weights[c["word"]],reverse=True)
    def top(self,n=5): return self.ranked()[:n]
    def best_question(self):
        best=None; bestscore=-1
        for key in QUESTIONS:
            if key in self.asked: continue
            y=n=u=0
            for c in self.concepts:
                w=self.weights[c["word"]]; v=c["attributes"].get(key)
                if v is True:y+=w
                elif v is False:n+=w
                else:u+=w
            coverage=y+n
            if coverage<.15:continue
            p=y/(y+n)
            h=sum(-q*math.log2(q) for q in (p,1-p) if q>0)
            score=h*coverage
            if score>bestscore:best,bestscore=key,score
        return best
    def count(self): return sum(v>.0005 for v in self.weights.values())

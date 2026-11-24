import json, os, urllib.request, urllib.error
from .questions import QUESTIONS

def enrich(word, model=None):
    model=model or os.getenv("OLLAMA_MODEL","mistral")
    url=os.getenv("OLLAMA_URL","http://localhost:11434").rstrip("/")
    keys={k:"true, false, or null" for k in QUESTIONS}
    prompt=("Return only JSON with an 'attributes' object. For concept "+repr(word)+
      ", assign true/false only when generally accurate, otherwise null. Keys: "+json.dumps(keys))
    data=json.dumps({"model":model,"prompt":prompt,"stream":False,"format":"json",
                     "options":{"temperature":0.1}}).encode()
    req=urllib.request.Request(url+"/api/generate",data=data,headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=90) as r: result=json.loads(r.read().decode())
    except urllib.error.URLError as e:
        raise RuntimeError("Cannot reach Ollama. Start Ollama and check OLLAMA_URL. "+str(e))
    parsed=json.loads(result.get("response","{}"))
    attrs=parsed.get("attributes",parsed)
    return {k:(attrs.get(k) if attrs.get(k) in (True,False,None) else None) for k in QUESTIONS}

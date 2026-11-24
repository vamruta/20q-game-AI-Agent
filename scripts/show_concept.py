import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from twentyq.knowledge import KnowledgeBase
kb=KnowledgeBase()
try:
    c=kb.resolve(" ".join(sys.argv[1:]))
    if not c: print("Not found")
    else:
        print(c["word"])
        for k,v in c["attributes"].items(): print(f" {k}: {v}")
finally:kb.close()

import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from twentyq.knowledge import KnowledgeBase,normalize_word
from twentyq.ollama_client import enrich
p=argparse.ArgumentParser(); p.add_argument("word"); p.add_argument("--model")
a=p.parse_args(); word=normalize_word(a.word); kb=KnowledgeBase()
try:
    attrs=enrich(word,a.model); kb.upsert(word,attrs,"ollama",.72)
    print("Added/updated:",word)
    print("AI properties are estimates; review with scripts/show_concept.py",word)
finally:kb.close()

from .knowledge import KnowledgeBase, normalize_word
from .engine import Engine, normalize_response
from .questions import QUESTIONS

def ask(prompt):
    try:return input(prompt).strip()
    except (EOFError,KeyboardInterrupt):
        print("\nExiting."); raise SystemExit

def learn(kb,word):
    print(f"'{word}' is not indexed yet.")
    if ask("Try to learn it now with Ollama/Mistral? [y/n] ").casefold() not in ("y","yes"):
        print("You can add it later: python scripts/enrich_word.py "+repr(word)); return
    try:
        from .ollama_client import enrich
        attrs=enrich(word)
        kb.upsert(word,attrs,"ollama",.72)
        print(f"Added '{word}'. AI-generated properties are estimates; review them.")
    except Exception as e:
        print("Learning failed:",e)
        print("Retry later: python scripts/enrich_word.py "+repr(word))

def play(kb):
    concepts=[c for c in kb.all() if sum(v is not None for v in c["attributes"].values())>=2]
    if not concepts: print("No described concepts yet."); return
    print("\n=== 20Q AI — Version 2.0 ===")
    print("Knowledge base:",len(concepts),"described concepts")
    print("Think of something. Answers: yes / probably yes / sometimes / probably no / no / unknown.")
    game=Engine(concepts)
    for i in range(1,21):
        key=game.best_question()
        if not key: break
        print(f"\nQuestion {i}/20: {QUESTIONS[key]}")
        response=normalize_response(ask("[yes/probably yes/sometimes/probably no/no/unknown] "))
        while response not in ("yes","probably yes","sometimes","probably no","no","unknown"):
            print("Please use one of the listed answers.")
            response=normalize_response(ask("> "))
        game.answer(key,response)
        best=game.ranked()[0]
        print(f"  (best candidate: {best['word']}; {game.count()} candidates with non-trivial weight)")
        if i>=5 and game.weights[best["word"]]>.55: break
    guesses=game.top()
    print("\nMy best remaining guesses:")
    for i,c in enumerate(guesses,1):
        print(f"  {i}. {c['word']}  (relative score {game.weights[c['word']]*100:.1f}%)")
    choice=ask("Was one of these your answer? Enter its number, or 0: ")
    if choice.isdigit() and 1<=int(choice)<=len(guesses):
        print("Great! Thanks for playing."); return
    word=normalize_word(ask("\nWhat were you thinking of? "))
    if not word:return
    found=kb.resolve(word)
    if not found:
        learn(kb,word); return
    print(f"'{word}' is already known as '{found['word']}'.")
    conflicts=[]
    for key,resp in game.history:
        val=found["attributes"].get(key)
        if val is None or resp in ("unknown","sometimes"): continue
        if (resp=="yes" and val is False) or (resp=="no" and val is True):
            conflicts.append((key,resp))
    if conflicts:
        print("Possible database mismatches:")
        for i,(key,resp) in enumerate(conflicts,1): print(f" {i}. {QUESTIONS[key]} (database says {'yes' if found['attributes'][key] else 'no'})")
        pick=ask("Number to correct, or Enter to skip: ")
        if pick.isdigit() and 1<=int(pick)<=len(conflicts):
            key,resp=conflicts[int(pick)-1]
            kb.update(word,key,resp=="yes")
            print("Corrected. Thanks for helping the game learn.")
    else: print("No obvious property conflict found.")

def main():
    kb=KnowledgeBase()
    try:
        print("20Q AI v2.0 — local knowledge base")
        while True:
            play(kb)
            if ask("\nPlay again? [] ").casefold() not in ("y","yes"):break
        print("Goodbye.")
    finally:kb.close()

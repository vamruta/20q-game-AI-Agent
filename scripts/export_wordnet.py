from pathlib import Path
import re
import nltk
from nltk.corpus import wordnet as wn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "wordnet_words.txt"

def main():
    try:
        wn.synsets("dog")
    except LookupError:
        nltk.download("wordnet")
        nltk.download("omw-1.4")

    words = set()
    for lemma in wn.all_lemma_names():
        word = lemma.replace("_", " ").lower().strip()
        # Keep English-like alphabetic terms; multiword concepts are allowed.
        if word and re.fullmatch(r"[a-z][a-z -]*", word):
            words.add(word)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")
    print(f"Exported {len(words):,} vocabulary entries to {OUT}")
    print("These are vocabulary entries, not yet semantically enriched candidates.")

if __name__ == "__main__":
    main()

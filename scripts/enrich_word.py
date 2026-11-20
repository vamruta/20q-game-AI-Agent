from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from twentyq.knowledge import KnowledgeBase
from twentyq.ollama_client import enrich_concept

def main():
    parser = argparse.ArgumentParser(description="Add a word using Ollama/Mistral.")
    parser.add_argument("word", help="English word or concept to enrich")
    parser.add_argument("--model", default=None, help="Ollama model name (default: mistral)")
    args = parser.parse_args()

    print(f"Generating attributes for {args.word!r}...")
    attrs = enrich_concept(args.word, args.model)
    print("\nGenerated properties:")
    for key, value in attrs.items():
        print(f"  {key}: {value}")

    confirm = input("\nSave these AI-generated properties? (y/n): ").strip().lower()
    if confirm in {"y", "yes"}:
        kb = KnowledgeBase()
        kb.upsert(args.word, attrs, source="ollama-generated", confidence=0.55)
        print("Saved to SQLite.")
    else:
        print("Not saved.")

if __name__ == "__main__":
    main()

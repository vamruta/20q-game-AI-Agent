from .knowledge import KnowledgeBase
from .game import GameSession

def main():
    kb = KnowledgeBase()
    print("\n=== 20Q AI — prototype ===")
    print(f"Knowledge base: {kb.count_words()} concepts")
    print("Think of a concept. Answer yes / no / sometimes / unknown.\n")

    game = GameSession(kb)
    while len(game.asked) < game.max_questions:
        if len(game.candidates) == 0:
            print("\nI have eliminated every known candidate.")
            break

        if len(game.candidates) == 1:
            guess = next(iter(game.candidates))
            answer = input(f"\nAre you thinking of {guess}? (y/n): ").strip().lower()
            if answer in {"y", "yes"}:
                print("Got it!")
                return
            print("I missed. This concept may need to be added or corrected.")
            break

        item = game.next_question()
        if not item:
            break
        key, question = item
        print(f"Question {len(game.asked) + 1}/{game.max_questions}: {question}")
        answer = input("[yes/no/sometimes/unknown] ").strip().lower()
        if answer in {"y", "yep"}:
            answer = "yes"
        elif answer in {"n", "nope"}:
            answer = "no"
        try:
            remaining = game.answer(key, answer)
        except ValueError as exc:
            print(exc)
            game.asked.discard(key)
            game.history.pop()
            continue
        print(f"  ({remaining} candidates remain)\n")

    guesses = game.guesses()
    if guesses:
        print("My best remaining guesses:")
        for index, word in enumerate(guesses, 1):
            print(f"  {index}. {word}")
        answer = input("Was one of these your answer? Enter its number, or 0: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(guesses):
            print("Excellent! The prototype's guess list helped.")
            return

    actual = input("\nWhat were you thinking of? ").strip()
    if actual:
        if kb.get(actual):
            print("That concept is already in the knowledge base.")
        else:
            print(
                f"'{actual}' is not indexed yet. Run scripts/enrich_word.py "
                "to add its semantic properties with Ollama."
            )

if __name__ == "__main__":
    main()

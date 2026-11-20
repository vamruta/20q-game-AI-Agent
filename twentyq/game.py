"""Information-gain question selection and a single game session."""
from __future__ import annotations
import math
from .questions import QUESTIONS

def binary_entropy(p: float) -> float:
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

def choose_question(candidates: dict, asked: set[str]):
    """Return the property with the best approximate information gain.

    Unknown values are retained as possible candidates for either answer.
    The score rewards balanced known splits and penalizes poor attribute coverage.
    """
    if len(candidates) < 2:
        return None

    best_key, best_score = None, -1.0
    total = len(candidates)

    for key in QUESTIONS:
        if key in asked:
            continue
        yes_count = sum(attrs.get(key) is True for attrs in candidates.values())
        no_count = sum(attrs.get(key) is False for attrs in candidates.values())
        known = yes_count + no_count
        if known < 2 or yes_count == 0 or no_count == 0:
            continue

        p_yes = yes_count / known
        coverage = known / total
        score = binary_entropy(p_yes) * coverage

        if score > best_score:
            best_key, best_score = key, score

    return best_key

class GameSession:
    def __init__(self, knowledge_base, max_questions=20):
        self.kb = knowledge_base
        self.max_questions = max_questions
        self.candidates = {
            word: attrs for word, attrs in self.kb.get_all().items()
            if any(value is not None for value in attrs.values())
        }
        self.asked = set()
        self.history = []
        self.finished = False

    def next_question(self):
        if self.finished:
            return None
        if len(self.candidates) <= 1:
            return None
        key = choose_question(self.candidates, self.asked)
        return (key, QUESTIONS[key]) if key else None

    def answer(self, key: str, answer: str):
        if self.finished:
            raise RuntimeError("Game is already finished")
        if key not in QUESTIONS or key in self.asked:
            raise ValueError("Invalid or repeated question")
        answer = answer.strip().lower()
        if answer not in {"yes", "no", "sometimes", "unknown"}:
            raise ValueError("Answer must be yes, no, sometimes, or unknown")

        self.asked.add(key)
        self.history.append((key, answer))

        if answer in {"yes", "no"}:
            expected = answer == "yes"
            # Unknown attributes are preserved: lack of knowledge is not a "no".
            self.candidates = {
                word: attrs for word, attrs in self.candidates.items()
                if attrs.get(key) is None or attrs.get(key) is expected
            }
        # "sometimes" and "unknown" do not eliminate candidates in this MVP.

        if len(self.asked) >= self.max_questions:
            self.finished = True

        return len(self.candidates)

    def guesses(self, limit=5):
        """Rank candidates by how well they agree with known answers."""
        def score(item):
            word, attrs = item
            matches = 0
            contradictions = 0
            for key, answer in self.history:
                value = attrs.get(key)
                if answer in ("yes", "no") and value is not None:
                    if value is (answer == "yes"):
                        matches += 1
                    else:
                        contradictions += 1
            return (matches - contradictions * 2, matches, word)
        return [
            word for word, _ in sorted(
                self.candidates.items(), key=score, reverse=True
            )[:limit]
        ]

    def make_guess(self, word):
        if word.lower() in self.candidates:
            self.finished = True
            return True
        return False

import tempfile
import unittest
from pathlib import Path

from twentyq.knowledge import KnowledgeBase
from twentyq.game import GameSession, choose_question

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.kb = KnowledgeBase(Path(self.tmp.name) / "test.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_seed_loaded(self):
        self.assertGreater(self.kb.count_words(), 10)

    def test_yes_answer_keeps_true_and_unknown(self):
        game = GameSession(self.kb)
        key = "electronic"
        game.answer(key, "yes")
        self.assertIn("microwave", game.candidates)
        self.assertIn("clock", game.candidates)  # unknown stays possible
        self.assertNotIn("dog", game.candidates)

    def test_question_selection(self):
        candidates = self.kb.get_all()
        question = choose_question(candidates, set())
        self.assertIn(question, self.kb.get("dog"))

if __name__ == "__main__":
    unittest.main()

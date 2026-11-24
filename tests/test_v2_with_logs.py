"""V2 regression tests with append-only interaction logs.
Run from project root:
  python -m unittest discover -s tests -p 'test_v2_with_logs.py' -v
Logs: logs/test_interactions.jsonl and logs/test_transcripts.txt
"""
import builtins, contextlib, io, json, logging, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
JSON_LOG = LOG_DIR / 'test_interactions.jsonl'
TEXT_LOG = LOG_DIR / 'test_transcripts.txt'
logger = logging.getLogger('20q_v2_test')
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    h = logging.FileHandler(JSON_LOG, encoding='utf-8')
    h.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(h)

def event(kind, **data):
    row = {'time_utc': datetime.now(timezone.utc).isoformat(), 'event': kind,
           'suite': '20q-ai-v2', **data}
    logger.info(json.dumps(row, ensure_ascii=False))

class ScriptedInput:
    def __init__(self, values, scenario):
        self.values, self.scenario = iter(values), scenario
    def __call__(self, prompt=''):
        value = next(self.values, '')
        event('input', scenario=self.scenario, prompt=prompt, value=value)
        with TEXT_LOG.open('a', encoding='utf-8') as f:
            f.write(f'[INPUT] {prompt}{value}\n')
        return value

class TestV2WithLogs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='20q_test_')
        self.db = Path(self.tmp.name) / 'test.db'
        event('test_start', test=self.id())
    def tearDown(self):
        event('test_end', test=self.id(), status='complete')
        self.tmp.cleanup()

    def test_normalization_and_answer_aliases(self):
        from twentyq.knowledge import normalize_word
        from twentyq.engine import normalize_response
        word = normalize_word('  Book\\  ')
        answer = normalize_response('maybe')
        event('normalization_check', input='Book\\', word=word,
              answer_input='maybe', answer=answer,
              passed=(word == 'book' and answer == 'sometimes'))
        self.assertEqual(word, 'book')
        self.assertEqual(answer, 'sometimes')

    def test_unknown_is_no_evidence_and_sometimes_keeps_candidates(self):
        from twentyq.engine import Engine
        concepts = [
            {'word':'telescope','attributes':{'has_lens':True},'confidence':.9},
            {'word':'hammer','attributes':{'has_lens':False},'confidence':.9},
        ]
        engine = Engine(concepts)
        before = dict(engine.weights)
        engine.answer('has_lens', 'unknown')
        event('engine_answer', question='has_lens', answer='unknown',
              weights_before=before, weights_after=engine.weights)
        self.assertEqual(before, engine.weights)
        engine.answer('portable', 'sometimes')
        event('engine_answer', question='portable', answer='sometimes',
              candidate_weights=engine.weights)
        self.assertTrue(all(v > 0 for v in engine.weights.values()))

    def test_v1_database_migration_preserves_data(self):
        import sqlite3
        from twentyq.knowledge import KnowledgeBase
        conn = sqlite3.connect(self.db)
        conn.execute('CREATE TABLE concepts(word TEXT PRIMARY KEY, attributes_json TEXT)')
        conn.execute('INSERT INTO concepts VALUES(?,?)', ('book','{"man_made": true}'))
        conn.commit(); conn.close()
        kb = KnowledgeBase(self.db)
        try:
            found = kb.resolve('book')
            event('migration', preserved=found is not None, concept=found)
            self.assertIsNotNone(found)
            self.assertTrue(found['attributes']['man_made'])
        finally:
            kb.close()

    def test_scripted_game_writes_transcript(self):
        from twentyq.knowledge import KnowledgeBase
        from twentyq import game
        kb = KnowledgeBase(self.db)
        try:
            kb.upsert('telescope', {
                'man_made':True, 'portable':True, 'vehicle':False,
                'is_tool':True, 'has_lens':True, 'used_for_viewing':True,
                'magnifies':True, 'used_for_astronomy':True,
            }, source='test-fixture', confidence=.95)
            # 20 unknown responses, select no guess, provide telescope, decline Ollama.
            scripted = ScriptedInput(['unknown']*5 + ['0','telescope'],
                                    'unknown_answers_then_telescope')
            captured = io.StringIO()
            with TEXT_LOG.open('a', encoding='utf-8') as f:
                f.write('\n=== SCRIPTED GAME ===\n')
            with patch.object(builtins, 'input', scripted), contextlib.redirect_stdout(captured):
                game.play(kb)
            output = captured.getvalue()
            with TEXT_LOG.open('a', encoding='utf-8') as f:
                f.write('[GAME OUTPUT]\n' + output + '\n')
            passed = "already known as 'telescope'" in output.lower() and 'telescope' in output.lower()
            event('game_transcript', scenario=scripted.scenario,
                  answer='telescope', output=output, passed=passed)
            self.assertTrue(passed, 'Scripted game did not reach answer feedback.')
        finally:
            kb.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)

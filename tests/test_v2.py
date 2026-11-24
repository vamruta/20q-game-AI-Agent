import tempfile,unittest
from pathlib import Path
from twentyq.knowledge import KnowledgeBase,normalize_word
from twentyq.engine import Engine,normalize_response
class Tests(unittest.TestCase):
 def test_backslash(self): self.assertEqual(normalize_word(" book\\\\ "),"book")
 def test_synonyms(self): self.assertEqual(normalize_response("maybe"),"sometimes")
 def test_unknown_no_change(self):
  e=Engine([{"word":"cat","attributes":{"animal":True}},{"word":"car","attributes":{"animal":False}}])
  before=e.weights.copy();e.answer("animal","unknown");self.assertEqual(before,e.weights)
 def test_alias(self):
  with tempfile.TemporaryDirectory() as d:
   k=KnowledgeBase(Path(d)/"x.db")
   try:
    k.upsert("plane",{"vehicle":True});self.assertTrue(k.alias("jetliner","plane"))
    self.assertEqual(k.resolve("jetliner")["word"],"plane")
   finally:k.close()
 def test_old_db_migration(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"old.db"
   import sqlite3
   db=sqlite3.connect(p);db.execute("CREATE TABLE concepts(word TEXT PRIMARY KEY, attributes_json TEXT)");db.execute("INSERT INTO concepts VALUES('book','{}')");db.commit();db.close()
   k=KnowledgeBase(p)
   try:self.assertIsNotNone(k.resolve("book"))
   finally:k.close()
if __name__=="__main__":unittest.main()

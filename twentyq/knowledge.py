import json, re, sqlite3, unicodedata
from pathlib import Path
from .questions import QUESTIONS

def normalize_word(s):
    s = unicodedata.normalize("NFKC", str(s or "")).strip().casefold()
    s = re.sub(r"\s+", " ", s)
    return re.sub(r"^[\W_]+|[\W_]+$", "", s, flags=re.UNICODE)


class KnowledgeBase:
    def __init__(self, path="data/knowledge.db"):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path)); self.db.row_factory = sqlite3.Row
        self.migrate(); self.seed()

    def close(self): self.db.close()

    def migrate(self):
        self.db.execute("""CREATE TABLE IF NOT EXISTS concepts(
          word TEXT PRIMARY KEY COLLATE NOCASE,
          attributes_json TEXT NOT NULL DEFAULT '{}',
          source TEXT NOT NULL DEFAULT 'legacy',
          confidence REAL NOT NULL DEFAULT 0.75)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS aliases(
          alias TEXT PRIMARY KEY COLLATE NOCASE, canonical_word TEXT NOT NULL COLLATE NOCASE)""")
        cols = {r["name"] for r in self.db.execute("PRAGMA table_info(concepts)")}
        for col, decl in [("source","TEXT NOT NULL DEFAULT 'legacy'"),("confidence","REAL NOT NULL DEFAULT 0.75")]:
            if col not in cols: self.db.execute(f"ALTER TABLE concepts ADD COLUMN {col} {decl}")
        self.db.commit()

    def get_exact(self, word):
        w = normalize_word(word)
        if not w: return None
        r = self.db.execute("SELECT * FROM concepts WHERE word=?", (w,)).fetchone()
        return self.row(r) if r else None

    def row(self, r):
        try: attrs = json.loads(r["attributes_json"] or "{}")
        except Exception: attrs = {}
        return {"word":r["word"], "attributes":attrs, "source":r["source"], "confidence":float(r["confidence"])}

    def resolve(self, word):
        w = normalize_word(word)
        c = self.get_exact(w)
        if c: return c
        r = self.db.execute("SELECT canonical_word FROM aliases WHERE alias=?", (w,)).fetchone()
        return self.get_exact(r["canonical_word"]) if r else None

    def all(self):
        return [self.row(r) for r in self.db.execute("SELECT * FROM concepts ORDER BY word")]

    def upsert(self, word, attrs, source="manual", confidence=.8):
        w = normalize_word(word)
        if not w: raise ValueError("Concept name is empty")
        clean = {k:v for k,v in attrs.items() if k in QUESTIONS and v in (True,False,None)}
        old = self.get_exact(w)
        if old:
            merged = old["attributes"].copy()
            merged.update({k:v for k,v in clean.items() if v is not None})
            clean = merged
        self.db.execute("""INSERT INTO concepts(word,attributes_json,source,confidence) VALUES(?,?,?,?)
          ON CONFLICT(word) DO UPDATE SET attributes_json=excluded.attributes_json,
          source=excluded.source, confidence=MAX(concepts.confidence,excluded.confidence)""",
          (w,json.dumps(clean),source,max(0,min(1,float(confidence)))))
        self.db.commit()
        return self.get_exact(w)

    def alias(self, alias, canonical):
        a,c = normalize_word(alias),normalize_word(canonical)
        if not a or a==c or not self.get_exact(c) or self.get_exact(a): return False
        self.db.execute("INSERT OR REPLACE INTO aliases VALUES(?,?)",(a,c)); self.db.commit()
        return True

    def update(self, word, key, value):
        c=self.resolve(word)
        if not c or key not in QUESTIONS or value not in (True,False,None): return False
        a=c["attributes"].copy(); a[key]=value
        self.upsert(c["word"],a,"user-corrected",1.0); return True

    def seed(self):
        if self.db.execute("SELECT COUNT(*) FROM concepts").fetchone()[0] == 0:
            seed = {
             "screwdriver":{"man_made":1,"portable":1,"vehicle":0,"electronic":0,"is_tool":1,"used_for_work":1},
             "hammer":{"man_made":1,"portable":1,"vehicle":0,"electronic":0,"is_tool":1,"used_for_work":1},
             "key":{"man_made":1,"portable":1,"vehicle":0,"electronic":0,"is_tool":1,"used_for_work":1},
             "book":{"man_made":1,"portable":1,"vehicle":0,"electronic":0,"is_tool":0,"used_for_work":1},
             "telescope":{"man_made":1,"portable":1,"vehicle":0,"is_tool":1,"has_lens":1,"used_for_viewing":1,"magnifies":1,"used_for_astronomy":1},
             "plane":{"man_made":1,"portable":0,"vehicle":1,"electronic":1,"has_wheels":1,"has_engine":1},
             "airplane":{"man_made":1,"portable":0,"vehicle":1,"electronic":1,"has_wheels":1,"has_engine":1},
             "dog":{"alive":1,"animal":1,"plant":0,"man_made":0,"has_body":1},
             "cat":{"alive":1,"animal":1,"plant":0,"man_made":0,"has_body":1},
             "finger":{"alive":0,"animal":0,"plant":0,"man_made":0,"part_of_body":1,"attached_to_body":1,"has_body":0},
             "smartphone":{"man_made":1,"portable":1,"electronic":1,"has_screen":1,"used_for_communication":1},
             "car":{"man_made":1,"portable":0,"vehicle":1,"has_wheels":1,"has_engine":1},
             "bicycle":{"man_made":1,"portable":0,"vehicle":1,"has_wheels":1,"has_engine":0},
             "tree":{"alive":1,"plant":1,"animal":0,"man_made":0,"natural":1},
             "apple":{"edible":1,"is_food":1,"natural":1},
             "knife":{"man_made":1,"portable":1,"is_tool":1,"used_for_cutting":1},
             "pencil":{"man_made":1,"portable":1,"is_tool":1,"used_for_writing":1},
             "microwave":{"man_made":1,"portable":0,"electronic":1,"used_for_cooking":1,"found_indoors":1},
             "television":{"man_made":1,"portable":0,"electronic":1,"has_screen":1,"used_for_viewing":1},
             "boat":{"man_made":1,"portable":0,"vehicle":1,"found_in_water":1},
             "helicopter":{"man_made":1,"portable":0,"vehicle":1,"has_engine":1},
            }
            for word,a in seed.items():
                self.upsert(word,{k:bool(v) for k,v in a.items()},"seed",.9)
        for a,c in [("aeroplane","plane"),("mobile phone","smartphone"),("cell phone","smartphone"),("mobile","smartphone"),("tv","television")]:
            if not self.get_exact(a): self.alias(a,c)

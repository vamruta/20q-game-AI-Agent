"""SQLite-backed semantic knowledge store."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

from .questions import QUESTIONS

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "knowledge.db"

# A small starter set: enough to play immediately and demonstrate the engine.
# Values: True, False, or None (unknown/ambiguous).
SEED = {
    "dog": dict(alive=True, animal=True, plant=False, man_made=False, electronic=False,
                portable=True, edible=False, vehicle=False, found_indoors=True,
                found_in_water=False, used_for_work=True, has_wheels=False,
                has_engine=False, is_food=False, is_tool=False),
    "cat": dict(alive=True, animal=True, plant=False, man_made=False, electronic=False,
                portable=True, edible=False, vehicle=False, found_indoors=True,
                found_in_water=False, used_for_work=False, has_wheels=False,
                has_engine=False, is_food=False, is_tool=False),
    "dolphin": dict(alive=True, animal=True, plant=False, man_made=False, electronic=False,
                    portable=False, edible=False, vehicle=False, found_indoors=False,
                    found_in_water=True, used_for_work=False, has_wheels=False,
                    has_engine=False, is_food=False, is_tool=False),
    "eagle": dict(alive=True, animal=True, plant=False, man_made=False, electronic=False,
                  portable=False, edible=False, vehicle=False, found_indoors=False,
                  found_in_water=False, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=False, is_tool=False),
    "rose": dict(alive=True, animal=False, plant=True, man_made=False, electronic=False,
                 portable=True, edible=None, vehicle=False, found_indoors=True,
                 found_in_water=False, used_for_work=False, has_wheels=False,
                 has_engine=False, is_food=False, is_tool=False),
    "oak tree": dict(alive=True, animal=False, plant=True, man_made=False, electronic=False,
                     portable=False, edible=None, vehicle=False, found_indoors=False,
                     found_in_water=False, used_for_work=False, has_wheels=False,
                     has_engine=False, is_food=False, is_tool=False),
    "apple": dict(alive=False, animal=False, plant=False, man_made=False, electronic=False,
                  portable=True, edible=True, vehicle=False, found_indoors=True,
                  found_in_water=False, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=True, is_tool=False),
    "bread": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                  portable=True, edible=True, vehicle=False, found_indoors=True,
                  found_in_water=False, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=True, is_tool=False),
    "pizza": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                  portable=True, edible=True, vehicle=False, found_indoors=True,
                  found_in_water=False, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=True, is_tool=False),
    "water": dict(alive=False, animal=False, plant=False, man_made=False, electronic=False,
                  portable=True, edible=True, vehicle=False, found_indoors=True,
                  found_in_water=True, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=True, is_tool=False),
    "microwave": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                      portable=True, edible=False, vehicle=False, found_indoors=True,
                      found_in_water=False, used_for_work=False, has_wheels=False,
                      has_engine=False, is_food=False, is_tool=False),
    "smartphone": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                       portable=True, edible=False, vehicle=False, found_indoors=True,
                       found_in_water=False, used_for_work=True, has_wheels=False,
                       has_engine=False, is_food=False, is_tool=False),
    "laptop": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                   portable=True, edible=False, vehicle=False, found_indoors=True,
                   found_in_water=False, used_for_work=True, has_wheels=False,
                   has_engine=False, is_food=False, is_tool=False),
    "television": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                       portable=False, edible=False, vehicle=False, found_indoors=True,
                       found_in_water=False, used_for_work=False, has_wheels=False,
                       has_engine=False, is_food=False, is_tool=False),
    "bicycle": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                    portable=False, edible=False, vehicle=True, found_indoors=False,
                    found_in_water=False, used_for_work=False, has_wheels=True,
                    has_engine=False, is_food=False, is_tool=False),
    "car": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                portable=False, edible=False, vehicle=True, found_indoors=False,
                found_in_water=False, used_for_work=True, has_wheels=True,
                has_engine=True, is_food=False, is_tool=False),
    "helicopter": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                       portable=False, edible=False, vehicle=True, found_indoors=False,
                       found_in_water=False, used_for_work=True, has_wheels=False,
                       has_engine=True, is_food=False, is_tool=False),
    "hammer": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                   portable=True, edible=False, vehicle=False, found_indoors=True,
                   found_in_water=False, used_for_work=True, has_wheels=False,
                   has_engine=False, is_food=False, is_tool=True),
    "screwdriver": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                        portable=True, edible=False, vehicle=False, found_indoors=True,
                        found_in_water=False, used_for_work=True, has_wheels=False,
                        has_engine=False, is_food=False, is_tool=True),
    "book": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                 portable=True, edible=False, vehicle=False, found_indoors=True,
                 found_in_water=False, used_for_work=True, has_wheels=False,
                 has_engine=False, is_food=False, is_tool=False),
    "chair": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                  portable=True, edible=False, vehicle=False, found_indoors=True,
                  found_in_water=False, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=False, is_tool=False),
    "table": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                  portable=False, edible=False, vehicle=False, found_indoors=True,
                  found_in_water=False, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=False, is_tool=False),
    "clock": dict(alive=False, animal=False, plant=False, man_made=True, electronic=None,
                  portable=True, edible=False, vehicle=False, found_indoors=True,
                  found_in_water=False, used_for_work=False, has_wheels=False,
                  has_engine=False, is_food=False, is_tool=False),
    "football": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                     portable=True, edible=False, vehicle=False, found_indoors=False,
                     found_in_water=False, used_for_work=False, has_wheels=False,
                     has_engine=False, is_food=False, is_tool=False),
    "guitar": dict(alive=False, animal=False, plant=False, man_made=True, electronic=None,
                   portable=True, edible=False, vehicle=False, found_indoors=True,
                   found_in_water=False, used_for_work=False, has_wheels=False,
                   has_engine=False, is_food=False, is_tool=False),
    "airplane": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                     portable=False, edible=False, vehicle=True, found_indoors=False,
                     found_in_water=False, used_for_work=True, has_wheels=True,
                     has_engine=True, is_food=False, is_tool=False),
    "boat": dict(alive=False, animal=False, plant=False, man_made=True, electronic=None,
                 portable=False, edible=False, vehicle=True, found_indoors=False,
                 found_in_water=True, used_for_work=True, has_wheels=False,
                 has_engine=None, is_food=False, is_tool=False),
    "computer": dict(alive=False, animal=False, plant=False, man_made=True, electronic=True,
                     portable=True, edible=False, vehicle=False, found_indoors=True,
                     found_in_water=False, used_for_work=True, has_wheels=False,
                     has_engine=False, is_food=False, is_tool=False),
    "key": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                portable=True, edible=False, vehicle=False, found_indoors=True,
                found_in_water=False, used_for_work=True, has_wheels=False,
                has_engine=False, is_food=False, is_tool=True),
    "orange": dict(alive=False, animal=False, plant=False, man_made=False, electronic=False,
                   portable=True, edible=True, vehicle=False, found_indoors=True,
                   found_in_water=False, used_for_work=False, has_wheels=False,
                   has_engine=False, is_food=True, is_tool=False),
    "bottle": dict(alive=False, animal=False, plant=False, man_made=True, electronic=False,
                   portable=True, edible=False, vehicle=False, found_indoors=True,
                   found_in_water=False, used_for_work=False, has_wheels=False,
                   has_engine=False, is_food=False, is_tool=False),
}

class KnowledgeBase:
    def __init__(self, db_path: Path | str = DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        if self.count_words() == 0:
            self.seed()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS concepts (
                    word TEXT PRIMARY KEY COLLATE NOCASE,
                    attributes_json TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'unknown',
                    confidence REAL NOT NULL DEFAULT 0.5
                )
            """)

    def seed(self):
        for word, attrs in SEED.items():
            self.upsert(word, attrs, source="starter", confidence=0.95)

    def upsert(self, word: str, attrs: dict, source="manual", confidence=0.7):
        word = " ".join(word.strip().lower().split())
        if not word:
            raise ValueError("Word cannot be empty")
        clean = {}
        for key in QUESTIONS:
            value = attrs.get(key)
            clean[key] = value if isinstance(value, bool) else None
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO concepts(word, attributes_json, source, confidence)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(word) DO UPDATE SET
                    attributes_json=excluded.attributes_json,
                    source=excluded.source,
                    confidence=excluded.confidence
            """, (word, json.dumps(clean), source, float(confidence)))

    def get_all(self):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT word, attributes_json FROM concepts ORDER BY word"
            ).fetchall()
        return {
            row["word"]: json.loads(row["attributes_json"])
            for row in rows
        }

    def get(self, word):
        return self.get_all().get(word.lower())

    def count_words(self):
        with self.connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]

    def import_word_list(self, path):
        """Import vocabulary spellings as placeholders; they are not guessable yet."""
        added = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if word and " " not in word and self.get(word) is None:
                    self.upsert(word, {}, source="vocabulary-only", confidence=0.0)
                    added += 1
        return added

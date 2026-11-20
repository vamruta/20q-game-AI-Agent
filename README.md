# 20Q AI — initial Python implementation

A hybrid 20 Questions game: deterministic candidate filtering + information-gain question selection, with optional Ollama/Mistral semantic enrichment.

## What works in this starter

- Terminal-playable guessing game.
- SQLite knowledge base.
- Information-gain question selection.
- `yes`, `no`, `sometimes`, and `unknown` answers.
- Optional Mistral/Ollama enrichment for new words.
- Optional WordNet vocabulary export.
- A small seed knowledge base so the game runs immediately.

## Important scope note

A dictionary is a vocabulary, not a complete set of facts. This starter can *store* a large dictionary vocabulary, but only words with useful semantic attributes can be reliably guessed. The included seed database is intentionally small. The next development step is to enrich more WordNet words, review uncertain attributes, and add more question dimensions.

Mistral-generated facts can be wrong. The game stores `null` for uncertain attributes and treats those as unknown rather than confidently eliminating a candidate.

## Requirements

- Python 3.10+
- Optional: Ollama installed and running, with a model such as `mistral` pulled.
- Optional: NLTK + WordNet corpus for vocabulary export.

## Run the game

From this directory:

```bash
python -m twentyq
```

## Enrich a word with Ollama

Start Ollama, then:

```bash
ollama pull mistral
pip install -r requirements-ollama.txt
python scripts/enrich_word.py "helicopter"
```

The generated properties are saved in `data/knowledge.db`. The script asks Mistral for JSON and validates the response shape. It cannot guarantee factual correctness.

You can configure another Ollama model:

```bash
OLLAMA_MODEL=mistral python scripts/enrich_word.py "gyroscope"
```

## Build a larger vocabulary list with WordNet

```bash
pip install -r requirements-wordnet.txt
python scripts/export_wordnet.py
```

This exports normalized single-word English lemmas to `data/wordnet_words.txt`. It does **not** automatically make every word guessable: words still need semantic properties.

## Project layout

```text
20q-ai/
├── twentyq/
│   ├── __init__.py
│   ├── __main__.py
│   ├── game.py
│   ├── knowledge.py
│   ├── questions.py
│   └── ollama_client.py
├── scripts/
│   ├── enrich_word.py
│   └── export_wordnet.py
├── tests/
│   └── test_engine.py
├── data/                 # created automatically
├── requirements-ollama.txt
├── requirements-wordnet.txt
└── README.md
```

## Current algorithm

For each unused question/property, the engine partitions remaining candidates into yes/no/unknown groups. It estimates the expected reduction in uncertainty and favors questions that split the known candidates evenly while covering a large fraction of the candidate set.

Unknown properties are not treated as "no". They remain possible after either answer, which is safer but can make the candidate set shrink more slowly.

## Android plan

Do not package Ollama into the first APK. First make the engine reliable. Then:

1. Add a Kivy UI around `GameSession`.
2. Keep SQLite locally on the phone.
3. For a connected-AI version, let the phone call Ollama on a PC over the same Wi-Fi network.
4. For fully offline Android AI, investigate a mobile inference runtime (for example llama.cpp) separately. Ollama itself is not a drop-in Android APK dependency.
5. Package the Kivy app with Buildozer on Linux (or WSL2).

The game engine is deliberately independent of Kivy so the UI can be replaced without rewriting the guessing logic.

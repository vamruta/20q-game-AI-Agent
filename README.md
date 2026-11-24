# 20Q AI — Version 2.0

Python 3.10+. The core game uses only the Python standard library.

## Run
```powershell
python -m twentyq
```

## Keep your old database
Copy your v1 `knowledge.db` into this project's `data` folder before first run:
```powershell
New-Item -ItemType Directory -Force data
Copy-Item "data\knowledge.db"
python -m twentyq
```
Version 2 adds tables if needed and preserves existing concept rows.

## Optional Ollama learning
```powershell
ollama pull mistral
python scripts/enrich_word.py telescope
```
Ollama must be running locally. Default model is `mistral`; set `$env:OLLAMA_MODEL` to change it.

## Tests
```powershell
python -m unittest discover -s tests -v
```

Answers: `yes`, `probably yes`, `sometimes`, `probably no`, `no`, `unknown`.
Unknown properties are not treated as false. Scores are relative rankings, not calibrated probabilities.

## Regression tests with interaction logs

Run this from the project folder in PowerShell:
```powershell
python -m unittest discover -s tests -p "test_v2_with_logs.py" -v
```

The test file appends structured events to `logs/test_interactions.jsonl` and a readable transcript to `logs/test_transcripts.txt`. It records simulated questions/answers, normalization results, candidate weights, migration checks, and the scripted game output. Logs persist between runs; review them before sharing.

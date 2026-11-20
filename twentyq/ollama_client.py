"""Optional Mistral/Ollama semantic enrichment."""
from __future__ import annotations
import json
import os
from .questions import QUESTIONS

def enrich_concept(word: str, model: str | None = None) -> dict:
    try:
        import ollama
    except ImportError as exc:
        raise RuntimeError(
            "Ollama Python package missing. Run: pip install -r requirements-ollama.txt"
        ) from exc

    model = model or os.getenv("OLLAMA_MODEL", "mistral")
    properties = list(QUESTIONS)
    schema = {
        "type": "object",
        "properties": {key: {"type": ["boolean", "null"]} for key in properties},
        "required": properties,
        "additionalProperties": False,
    }

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You create cautious factual attributes for a 20 Questions game. "
                    "Return only the requested JSON object. Use null when a property "
                    "depends on context, is ambiguous, or you are not confident. "
                    "Interpret each property in its ordinary, common meaning."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate attributes for the English concept: {word!r}. "
                    "For 'found_indoors', use commonly found indoors. "
                    "For 'portable', use whether one person can normally carry it. "
                    "For 'alive', use whether the concept itself is a living organism. "
                    "For 'is_food', include food or drink."
                ),
            },
        ],
        format=schema,
        options={"temperature": 0.1},
    )

    raw = response["message"]["content"]
    data = json.loads(raw)
    cleaned = {}
    for key in properties:
        value = data.get(key)
        cleaned[key] = value if isinstance(value, bool) else None
    return cleaned

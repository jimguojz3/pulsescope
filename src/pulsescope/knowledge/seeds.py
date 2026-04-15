import json
import os


def _seed_path() -> str:
    # Support both repo root and installed package contexts
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "seeds", "companies.json"),
        os.path.join(os.getcwd(), "data", "seeds", "companies.json"),
    ]
    for path in candidates:
        normalized = os.path.abspath(path)
        if os.path.exists(normalized):
            return normalized
    raise FileNotFoundError("Seed company data not found")


def load_seed_companies() -> list[dict]:
    with open(_seed_path(), "r", encoding="utf-8") as f:
        return json.load(f)

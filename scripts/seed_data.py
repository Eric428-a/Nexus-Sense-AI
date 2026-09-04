"""Seed deterministic development data."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"data/processed/seed.json"
out.write_text(json.dumps({"entities":[],"documents":[],"events":[]},indent=2),encoding="utf-8")
print(out)

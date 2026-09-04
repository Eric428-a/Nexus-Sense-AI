"""Bootstrap NEXUS-SENSE project directories."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for path in ["data/raw","data/processed","logs"]: (ROOT/path).mkdir(parents=True,exist_ok=True)
print("NEXUS-SENSE bootstrap complete")

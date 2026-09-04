"""Local healthcheck."""
import urllib.request
URL="http://127.0.0.1:8000/api/v1/health"
try:
    with urllib.request.urlopen(URL,timeout=3) as r: print(r.status, r.read().decode())
except Exception as exc: print(f"Healthcheck unavailable: {exc}")

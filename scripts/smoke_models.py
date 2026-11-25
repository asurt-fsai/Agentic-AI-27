"""T15 check: one call on each route, and the time each took."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.llm.models import get_model  # noqa: E402

routes = sys.argv[1:] or ["api", "local"]

for route in routes:
    start = time.time()
    try:
        reply = get_model(route).invoke("Reply with the single word OK").content
        print(f"[{route}] OK in {time.time() - start:.1f}s -> {reply!r}")
    except Exception as exc:  # show the error type so timeouts are visible
        print(f"[{route}] FAILED in {time.time() - start:.1f}s -> {type(exc).__name__}: {exc}")

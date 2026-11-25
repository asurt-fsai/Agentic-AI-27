import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.llm import models  # noqa: E402


def test_unknown_route_is_rejected():
    with pytest.raises(ValueError):
        models.get_model("nope")


def test_both_routes_exist():
    assert models.ROUTES == ("api", "local", "openrouter")


def test_timeouts_are_positive():
    assert models.API_TIMEOUT > 0
    assert models.LOCAL_TIMEOUT > 0


def test_models_build_without_network(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    assert models.get_model("api") is not None
    assert models.get_model("local") is not None
    assert models.get_model("openrouter") is not None

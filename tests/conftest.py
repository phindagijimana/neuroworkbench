from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _no_model_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "AZURE_OPENAI_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _reset_execute() -> None:
    from kernel.execute import reset_execute_calls

    reset_execute_calls()
    yield
    reset_execute_calls()

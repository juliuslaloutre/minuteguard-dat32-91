from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def load_json():
    def _load(relative_path: str) -> Any:
        return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))

    return _load


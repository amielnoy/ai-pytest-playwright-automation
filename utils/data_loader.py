import json
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"
_CONFIG_DIR = _PROJECT_ROOT / "config"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _data_path(filename: str) -> Path:
    return _DATA_DIR / filename


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _resolve_placeholders(section: Any) -> Any:
    if isinstance(section, dict):
        return {k: _resolve_placeholders(v) for k, v in section.items()}
    if isinstance(section, str) and "{ts}" in section:
        return section.replace("{ts}", uuid.uuid4().hex[:8])
    return section


@lru_cache(maxsize=1)
def _load_test_data_bundle() -> dict[str, Any]:
    merged = _load_json(_data_path("test_data.json"))
    secrets_path = _data_path("secrets.json")
    if secrets_path.exists() and secrets_path.stat().st_size > 0:
        merged = _deep_merge(merged, _load_json(secrets_path))
    return merged


def has_secret_file() -> bool:
    return _data_path("secrets.json").exists()


def get_test_data(key: str | None = None) -> Any:
    merged = _load_test_data_bundle()
    section = merged.get(key, {}) if key else merged
    return _resolve_placeholders(section)


@lru_cache(maxsize=1)
def get_config() -> dict:
    return _load_json(_CONFIG_DIR / "config.json")

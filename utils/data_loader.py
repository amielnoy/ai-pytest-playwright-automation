import json
import os
import uuid
import yaml
from typing import Any


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _data_path(filename: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", filename))


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


def _load_secrets() -> dict:
    path = _data_path("secrets.json")
    try:
        return _load_json(path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"secrets.json not found at {path}. "
            "Copy data/secrets.json.example → data/secrets.json and fill in your credentials."
        ) from None


def get_test_data(key: str | None = None) -> Any:
    merged = _deep_merge(_load_json(_data_path("test_data.json")), _load_secrets())
    section = merged.get(key, {}) if key else merged
    return _resolve_placeholders(section)


def get_config() -> dict:
    return _load_yaml(_data_path("../config/config.yaml"))

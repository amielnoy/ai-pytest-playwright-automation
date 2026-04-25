import json
import os
import time
import yaml
from typing import Any


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _data_path(filename: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", filename))


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base (override wins on conflicts)."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _resolve_placeholders(section: Any) -> Any:
    """Replace {ts} with the current Unix timestamp (unique per test run)."""
    if isinstance(section, dict):
        return {k: _resolve_placeholders(v) for k, v in section.items()}
    if isinstance(section, str) and "{ts}" in section:
        return section.replace("{ts}", str(int(time.time())))
    return section


def _load_secrets() -> dict:
    path = _data_path("secrets.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"secrets.json not found at {path}. "
            "Copy data/secrets.json.example → data/secrets.json and fill in your credentials."
        )
    return load_json(path)


def get_test_data(key: str = None) -> Any:
    """
    Return merged test data (test_data.json + secrets.json).
    secrets.json values take precedence so credentials stay out of VCS.
    """
    data = load_json(_data_path("test_data.json"))
    secrets = _load_secrets()
    merged = _deep_merge(data, secrets)

    if key:
        section = _resolve_placeholders(merged.get(key, {}))
        return section
    return _resolve_placeholders(merged)


def get_config() -> dict:
    return load_yaml(_data_path("../config/config.yaml"))

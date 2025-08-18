from pathlib import Path
import yaml


class ConfigError(Exception):
    pass


def load_config(path_str: str) -> dict:
    path = Path(path_str)
    if not path.exists():
        raise ConfigError(f"Config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    # Minimal defaults
    data.setdefault("outputs_dir", "./artifacts")
    return data

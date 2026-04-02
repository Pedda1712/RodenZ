import yaml
from pathlib import Path


def load_config(path: Path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_config(cfg, path: Path):
    with open(path, 'w') as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
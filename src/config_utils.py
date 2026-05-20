"""Utility functions for loading YAML configuration files."""

from pathlib import Path
import yaml


def load_yaml(path: str | Path) -> dict:
    """Load a YAML file and return it as a Python dictionary.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the parsed YAML content.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
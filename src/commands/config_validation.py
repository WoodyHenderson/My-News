from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

""" Validating YAML Configs. """

class ConfigValidationError(ValueError):
    """Raised when the configuration file is missing or invalid."""


def load_and_validate_config(config_path: Path) -> dict[str, Any]:
    """Load and validate YAML configuration from disk."""
    if not config_path.exists():
        raise ConfigValidationError(
            f"Configuration file {config_path} does not exist, try running 'mycli init' to create one."
        )

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config_data = yaml.safe_load(config_file)
    except yaml.YAMLError as exc:
        raise ConfigValidationError(
            f"Configuration file {config_path} is not valid YAML. Error: {exc}"
        ) from exc

    if config_data is None:
        raise ConfigValidationError(
            f"Configuration file {config_path} is empty. It must define at least the 'sources' key."
        )

    if not isinstance(config_data, dict):
        raise ConfigValidationError(
            f"Configuration file {config_path} must contain a top-level mapping/object."
        )

    if "sources" not in config_data:
        raise ConfigValidationError(
            f"Configuration file {config_path} is missing the 'sources' key."
        )

    return config_data

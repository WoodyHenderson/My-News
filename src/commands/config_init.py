from __future__ import annotations

from pathlib import Path
from shutil import copyfile


class ConfigInitError(ValueError):
    """Raised when the configuration file cannot be initialized."""


def initialize_config(
    config_path: Path,
    force: bool = False,
    default_config_path: Path = Path("config/default.yaml"),
) -> list[str]:
    """Initialize configuration by copying the base config."""

    if config_path.exists() and not force:
        raise ConfigInitError(
            f"Configuration file {config_path} already exists. Use --force to overwrite."
        )

    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        copyfile(default_config_path, config_path)
    except Exception as exc:
        raise ConfigInitError(f"Failed to initialize configuration. Error: {exc}") from exc

    if force:
        return [f"Base configuration file restored at {config_path}."]
    return [
        f"Base configuration file created at {config_path}. Add your interests and sources to customise it."
    ]

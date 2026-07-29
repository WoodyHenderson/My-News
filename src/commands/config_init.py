from __future__ import annotations

from pathlib import Path
from shutil import copyfile


class ConfigInitError(ValueError):
    """Raised when the configuration file cannot be initialized."""


def initialize_config(
    config_path: Path,
    force: bool = False,
    backups_dir: Path = Path("config/configbackups"),
    example_config_path: Path = Path("example.yaml"),
) -> list[str]:
    """Initialize configuration by restoring backup or copying the example file."""
    messages: list[str] = []

    if config_path.exists() and not force:
        raise ConfigInitError(
            f"Configuration file {config_path} already exists. Use --force to overwrite."
        )

    if not config_path.exists():
        messages.append(f"Configuration file not found at {config_path}. Trying to restore a backup")
        backups = sorted(backups_dir.glob("config_*.yaml"), reverse=True)

        if backups:
            latest_backup = backups[0]
            try:
                copyfile(latest_backup, config_path)
                messages.append(
                    f"Restored configuration from backup: {latest_backup} to {config_path}"
                )
            except Exception as exc:
                raise ConfigInitError(f"Failed to restore backup. Error: {exc}") from exc
        else:
            messages.append(f"No backup configuration files found in {backups_dir}.")

        try:
            copyfile(example_config_path, config_path)
            messages.append(
                f"Example configuration file created at {config_path}. RENAME to 'config.yaml' and customise"
            )
        except Exception as exc:
            raise ConfigInitError(f"Tf did u do bro. Error: {exc}") from exc

    return messages

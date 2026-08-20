from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

""" Validating YAML Configs. """

class ConfigValidationError(ValueError):
    """Raised when the configuration file is missing or invalid."""


def _load_category_interests(catalog_path: Path) -> list[dict[str, Any]]:
    """Load a category catalog file that contains one or more interests."""
    try:
        with open(catalog_path, "r", encoding="utf-8") as category_file:
            parsed = yaml.safe_load(category_file)
    except yaml.YAMLError as exc:
        raise ConfigValidationError(
            f"Category catalog file {catalog_path} is not valid YAML. Error: {exc}"
        ) from exc

    if parsed is None:
        return []

    if not isinstance(parsed, list):
        raise ConfigValidationError(
            f"Category catalog file {catalog_path} must contain a YAML list of interests."
        )

    for item in parsed:
        if not isinstance(item, dict):
            raise ConfigValidationError(
                f"Category catalog file {catalog_path} contains a non-object interest entry."
            )

    return parsed


def _append_unique_interests(
    config_data: dict[str, Any],
    interests_to_add: list[dict[str, Any]],
) -> None:
    """Append interests while avoiding duplicate ids in config_data."""
    existing_interests = config_data.get("interests")
    if existing_interests is None:
        existing_interests = []
        config_data["interests"] = existing_interests

    if not isinstance(existing_interests, list):
        raise ConfigValidationError("Configuration key 'interests' must be a list.")

    existing_ids = {
        interest.get("id")
        for interest in existing_interests
        if isinstance(interest, dict) and "id" in interest
    }

    for interest in interests_to_add:
        interest_id = interest.get("id")
        if interest_id in existing_ids:
            continue
        existing_interests.append(interest)
        existing_ids.add(interest_id)


def load_and_validate_config(
    config_path: Path,
    provider_pref: list[str] | None = None,
    category_pref: list[str] | None = None,
) -> dict[str, Any]:
    """Create a config by loading in user preferences and then validate."""
    if not config_path.exists():
        raise ConfigValidationError(
            f"Configuration file {config_path} does not exist, try running 'my-news init' to create one."
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
            f"Configuration file {config_path} is empty."
        )

    if not isinstance(config_data, dict):
        raise ConfigValidationError(
            f"Configuration file {config_path} must contain a top-level mapping/object."
        )

    if "sources" not in config_data:
        raise ConfigValidationError(
            f"Configuration file {config_path} is missing the 'sources' key."
        )

    # Merge selected category preferences from config catalog into interests.
    if category_pref:
        category_catalog_dir = (
            config_path.parent.parent / "config_catalog" / "categories"
        )
        for category in category_pref:
            category_key = category.strip()
            category_file = category_catalog_dir / f"{category_key}.yaml"
            if not category_file.exists():
                raise ConfigValidationError(
                    f"Category preference '{category}' does not map to a catalog file at {category_file}."
                )
            category_interests = _load_category_interests(category_file)
            _append_unique_interests(config_data, category_interests)

    return config_data

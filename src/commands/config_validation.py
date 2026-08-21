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


def _load_provider_feeds(catalog_path: Path) -> list[dict[str, Any]]:
    """Load a provider catalog file that contains one or more feeds."""
    try:
        with open(catalog_path, "r", encoding="utf-8") as provider_file:
            parsed = yaml.safe_load(provider_file)
    except yaml.YAMLError as exc:
        raise ConfigValidationError(
            f"Provider catalog file {catalog_path} is not valid YAML. Error: {exc}"
        ) from exc

    if parsed is None:
        return []

    if not isinstance(parsed, list):
        raise ConfigValidationError(
            f"Provider catalog file {catalog_path} must contain a YAML list of feeds."
        )

    feeds = []
    for provider in parsed:
        if not isinstance(provider, dict):
            raise ConfigValidationError(
                f"Provider catalog file {catalog_path} contains a non-object provider entry."
            )
        provider_id = provider.get("id")
        provider_feeds = provider.get("feeds", [])
        if isinstance(provider_feeds, list):
            for feed in provider_feeds:
                if not isinstance(feed, dict):
                    continue
                feed = feed.copy()
                feed_id = feed.get("id")
                if provider_id and feed_id and not feed_id.startswith(f"{provider_id}-"):
                    feed["id"] = f"{provider_id}-{feed_id}"
                feeds.append(feed)

    return feeds


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

    # If category preferences are provided, replace interests with only selected ones.
    # If None, keep the config's existing interests.
    if category_pref is not None:
        category_catalog_dir = (
            config_path.parent.parent / "config_catalog" / "categories"
        )
        selected_interests = []
        for category in category_pref:
            category_key = category.strip()
            category_file = category_catalog_dir / f"{category_key}.yaml"
            if not category_file.exists():
                raise ConfigValidationError(
                    f"Category preference '{category}' does not map to a catalog file at {category_file}."
                )
            category_interests = _load_category_interests(category_file)
            selected_interests.extend(category_interests)
        # Replace interests with only the selected ones (dedup by id)
        unique_interests = {}
        for interest in selected_interests:
            interest_id = interest.get("id")
            if interest_id:
                unique_interests[interest_id] = interest
        config_data["interests"] = list(unique_interests.values())

    # If provider preferences are provided, replace sources with only selected ones.
    # If None, keep the config's existing sources.
    if provider_pref is not None:
        provider_catalog_dir = (
            config_path.parent.parent / "config_catalog" / "publishers"
        )
        selected_sources = []
        for provider in provider_pref:
            provider_key = provider.strip()
            provider_file = provider_catalog_dir / f"{provider_key}.yaml"
            if not provider_file.exists():
                raise ConfigValidationError(
                    f"Provider preference '{provider}' does not map to a catalog file at {provider_file}."
                )
            provider_feeds = _load_provider_feeds(provider_file)
            selected_sources.extend(provider_feeds)
        # Replace sources with only the selected ones (dedup by id)
        unique_sources = {}
        for source in selected_sources:
            source_id = source.get("id")
            if source_id:
                unique_sources[source_id] = source
        config_data["sources"] = list(unique_sources.values())

    return config_data

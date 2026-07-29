from __future__ import annotations

import typer
from pathlib import Path
from typing import Annotated, Optional

from src.commands.config_init import ConfigInitError, initialize_config
from src.commands.config_validation import ConfigValidationError, load_and_validate_config

app = typer.Typer(
    name="mycli",
    help="A simple CLI application built with Typer.",
    no_args_is_help=True
)

sources_app = typer.Typer(help="Commands for discovering and managing sources")
app.add_typer(sources_app, name="sources")

_DEFAULT_CONFIG = Path("config/config.yaml")

@app.command()
def init (
    config: Annotated[Path, typer.Option("--config", "-c", help="Path to the configuration file")] = _DEFAULT_CONFIG,
    force: Annotated[bool, typer.Option("--force", "-f", help="Force overwrite of existing configuration file")] = False,
) -> None:
    """
    Initialize the application with a configuration file.
    """
    try:
        messages = initialize_config(config_path=config, force=force)
        for message in messages:
            typer.echo(message)
    except ConfigInitError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

@app.command()
def validate(
    config: Annotated[Path, typer.Option("--config", "-c", help="Path to the configuration file")] = _DEFAULT_CONFIG,
) -> None:
    """
    Validate the configuration file.
    """
    try:
        load_and_validate_config(config)
    except ConfigValidationError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

@app.command()
def run(
    config: Annotated[Path, typer.Option("--config", "-c", help="Path to the configuration file")] = _DEFAULT_CONFIG,
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Path to the output file")] = None,
) -> None:
    """
    Run the application with the specified configuration file and output path.
    """
    try:
        config_data = load_and_validate_config(config)
    except ConfigValidationError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)

    

from __future__ import annotations

import typer
from pathlib import Path
from typing import Annotated, Optional
from shutil import copyfile

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
    if config.exists() and not force:
        typer.echo(f"Configuration file {config} already exists. Use --force to overwrite.")
        raise typer.Exit(code=1)

    if not config.exists():
        typer.echo(f"Configuration file not found at {config}. Trying to restore a backup")
        backups_dir = Path("config/configbackups")
        backups = sorted(backups_dir.glob("config_*.yaml"), reverse=True)
        if backups:
            latest_backup = backups[0]
            try:
                copyfile(latest_backup, config)
                typer.echo(f"Restored configuration from backup: {latest_backup} to {config}")
            except Exception as e:
                typer.echo(f"Failed to restore backup. Error: {e}")
                raise typer.Exit(code=1)
        else:
            typer.echo(f"No backup configuration files found in {backups_dir}.")
        try:
            copyfile("example.yaml", config)
            typer.echo(f"Example configuration file created at {config}. RENAME to 'config.yaml' and customise")
        except Exception as e:
            typer.echo(f"Tf did u do bro. Error: {e}")
            raise typer.Exit(code=1)

@app.command()
def validate(
    config: Annotated[Path, typer.Option("--config", "-c", help="Path to the configuration file")] = _DEFAULT_CONFIG,
) -> None:
    """
    Validate the configuration file.
    """
    if not config.exists():
        typer.echo(f"Configuration file {config} does not exist.")
        raise typer.Exit(code=1)

    # Here you would add your validation logic for the configuration file
    # For demonstration purposes, we'll just print a success message
    typer.echo(f"Configuration file {config} is valid."
)
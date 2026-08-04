from __future__ import annotations

import typer
from pathlib import Path
from typing import Annotated, Optional

from src.commands.config_init import ConfigInitError, initialize_config
from src.commands.config_validation import ConfigValidationError, load_and_validate_config
from src.commands.config_run import ConfigRunError, run_application
from src.gui import main as run_gui
from src.seen_articles import canonicalise_url, mark_seen

""" CLI that we will use for interacting with the app. """

app = typer.Typer(
    name="mycli",
    help="A CLI is funnier than a frontend",
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
        typer.secho(str(e), fg="red")
        raise typer.Exit(code=1)
    typer.secho(f"Configuration file {config} initialized successfully.", fg="green")

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
        typer.secho(str(e), fg="red")
        raise typer.Exit(code=1)
    typer.secho(f"Configuration file {config} is valid.", fg="green")

@app.command()
def run(
    config: Annotated[Path, typer.Option("--config", "-c", help="Path to the configuration file")] = _DEFAULT_CONFIG,
    output: Annotated[Optional[Path], typer.Option("--output", "-o", help="Path to the output file")] = None,
) -> None:
    """
    Run the application with the specified configuration file and output path.
    """
    def _progress(msg: str, level: str) -> None:
        if level == "success":
            typer.secho(msg, fg="green")
        elif level == "error":
            typer.secho(msg, fg="red")
        else:
            typer.echo(msg)

    try:
        run_application(config_path=config, output_path=output, on_progress=_progress)
    except ConfigRunError as e:
        typer.secho(str(e), fg="red")
        raise typer.Exit(code=1)
    typer.secho(f"Configuration file {config} loaded successfully.", fg="green")

@app.command()
def markseen(
    url: Annotated[str, typer.Argument(help="Article URL to mark as seen")],
) -> None:
    """Mark an article URL as seen so it can be filtered from future digests."""
    inserted = mark_seen(url)
    canonical_url = canonicalise_url(url)
    if inserted:
        typer.secho(f"Marked as seen: {canonical_url}", fg="green")
    else:
        typer.secho(f"Already marked as seen: {canonical_url}", fg="yellow")

@app.command()
def opengui() -> None:
    """
    Open the GUI for the application.
    """
    run_gui()

if __name__ == "__main__":
    app()
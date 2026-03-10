import importlib
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Database seeding commands.")

SEEDERS_DIR = "seeders"


def _load_seeder_class(class_name: str):
    """
    Load a seeder class by name from the seeders/ directory.
    The seeder file must match the class name (e.g. UserSeeder → seeders/UserSeeder.py).
    """
    seeders_path = Path(SEEDERS_DIR)

    if not seeders_path.exists():
        typer.secho(
            f"  ✗  Seeders directory '{SEEDERS_DIR}/' not found. "
            f"Create it and add your seeder classes.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    seeder_file = seeders_path / f"{class_name}.py"
    if not seeder_file.exists():
        typer.secho(
            f"  ✗  Seeder file '{seeder_file}' not found.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    # Dynamically import the seeder module
    if str(seeders_path) not in sys.path:
        sys.path.insert(0, str(seeders_path))

    module = importlib.import_module(class_name)
    seeder_class = getattr(module, class_name, None)

    if seeder_class is None:
        typer.secho(
            f"  ✗  Class '{class_name}' not found in '{seeder_file}'. "
            f"Make sure the class name matches the file name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    return seeder_class


def _run_seeder(class_name: str) -> None:
    """Instantiate and run a single seeder class."""
    seeder_class = _load_seeder_class(class_name)

    if not hasattr(seeder_class, "run") or not callable(seeder_class.run):
        typer.secho(
            f"  ✗  '{class_name}' does not implement a run() method. "
            f"Every seeder must implement run().",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    try:
        instance = seeder_class()
        instance.run()
        typer.secho(f"  ✓  {class_name} completed.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"  ✗  {class_name} failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


def _discover_seeders() -> list[str]:
    """Discover all seeder classes in the seeders/ directory."""
    seeders_path = Path(SEEDERS_DIR)

    if not seeders_path.exists():
        return []

    return [
        f.stem for f in sorted(seeders_path.glob("*.py"))
        if f.stem != "__init__"
    ]


@app.callback(invoke_without_command=True)
def seed(seeder: str = typer.Argument(None, help="Specific seeder class to run (e.g. UserSeeder)")):
    """
    Run database seeders.

    \b
    Every seeder must be placed in the seeders/ directory and implement a run() method:

        # seeders/UserSeeder.py
        class UserSeeder:
            def run(self):
                # Insert seed data here
                pass

    \b
    Example:
        fastkit db seed               # Run all seeders
        fastkit db seed UserSeeder    # Run a specific seeder
    """
    typer.echo("")

    if seeder:
        typer.secho(f"Running seeder: {seeder}", fg=typer.colors.BRIGHT_CYAN, bold=True)
        typer.echo("")
        _run_seeder(seeder)
    else:
        seeders = _discover_seeders()

        if not seeders:
            typer.secho(
                "  ⚠  No seeders found in 'seeders/' directory.",
                fg=typer.colors.YELLOW,
            )
            raise typer.Exit(0)

        typer.secho(f"Running all seeders ({len(seeders)} found)...", fg=typer.colors.BRIGHT_CYAN, bold=True)
        typer.echo("")

        for seeder_name in seeders:
            _run_seeder(seeder_name)

    typer.echo("")
    typer.secho("Done!", fg=typer.colors.BRIGHT_WHITE, bold=True)
    typer.echo("")

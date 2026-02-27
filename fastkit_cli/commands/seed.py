import typer

app = typer.Typer(help="Database seeding commands.")


@app.command()
def seed(seeder: str = typer.Argument(None, help="Specific seeder class to run")):
    """Run database seeders."""
    if seeder:
        typer.echo(f"Running seeder: {seeder}")
    else:
        typer.echo("Running all seeders...")
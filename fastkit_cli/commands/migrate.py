import typer

app = typer.Typer(help="Migration commands.")


@app.command()
def run():
    """Run pending migrations. (alembic upgrade head)"""
    typer.echo("Running migrations...")


@app.command()
def make(message: str = typer.Option(..., "--message", "-m", help="Migration message")):
    """Generate a new migration. (alembic revision --autogenerate)"""
    typer.echo(f"Generating migration: {message}")


@app.command()
def rollback():
    """Rollback last migration. (alembic downgrade -1)"""
    typer.echo("Rolling back last migration...")


@app.command()
def status():
    """Show current migration status. (alembic current)"""
    typer.echo("Checking migration status...")
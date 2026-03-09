import subprocess
import sys

import typer

app = typer.Typer(help="Server commands.")


@app.callback(invoke_without_command=True)
def start(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload"),
    app_path: str = typer.Option("main:app", "--app", help="App module path (e.g. main:app)"),
):
    """Start the FastAPI development server."""
    typer.secho(f"Starting server on {host}:{port}...", fg=typer.colors.BRIGHT_CYAN, bold=True)

    cmd = [
        sys.executable, "-m", "uvicorn",
        app_path,
        "--host", host,
        "--port", str(port),
    ]

    if reload:
        cmd.append("--reload")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        typer.secho(
            "  ✗  uvicorn not found. Install it with: pip install uvicorn",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        typer.secho("\n  Server stopped.", fg=typer.colors.YELLOW)
    except subprocess.CalledProcessError as e:
        typer.secho(f"  ✗  Server exited with error: {e.returncode}", fg=typer.colors.RED)
        raise typer.Exit(e.returncode)
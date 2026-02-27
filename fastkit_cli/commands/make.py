import re
from enum import Enum
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader

app = typer.Typer(help="Code generation commands.")

# Path to templates folder (relative to this file)
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "module"

# Templates to generate for a full module
MODULE_TEMPLATES = [
    ("model.py.jinja", "models.py"),
    ("schemas.py.jinja", "schemas.py"),
    ("repository.py.jinja", "repository.py"),
    ("async_repository.py.jinja", "async_repository.py"),
    ("service.py.jinja", "service.py"),
    ("async_service.py.jinja", "async_service.py"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _to_snake_case(name: str) -> str:
    """Convert PascalCase or camelCase to snake_case. Example: InvoiceItem → invoice_item"""
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name)
    return name.lower()


def _to_pascal_case(name: str) -> str:
    """Convert snake_case or any string to PascalCase. Example: invoice_item → InvoiceItem"""
    return ''.join(word.capitalize() for word in re.split(r'[_\s-]', name))


def _to_plural(name: str) -> str:
    """
    Simple English pluralization for table names.
    Covers most common cases used in model naming.
    """
    if name.endswith('y') and not name.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
        return name[:-1] + 'ies'   # category → categories
    if name.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return name + 'es'          # status → statuses
    return name + 's'               # invoice → invoices


def _render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
    )
    template = env.get_template(template_name)
    return template.render(**context)


def _register_in_alembic(model_name: str, module_folder: str) -> None:
    """
    Register the new model in Alembic env.py so autogenerate detects it.
    Looks for env.py in alembic/ or migrations/ folder.
    """
    env_py = None
    for candidate in ["alembic/env.py", "migrations/env.py"]:
        path = Path(candidate)
        if path.exists():
            env_py = path
            break

    if env_py is None:
        typer.secho(
            "  ⚠  Could not find alembic/env.py or migrations/env.py. "
            "Please register the model manually.",
            fg=typer.colors.YELLOW,
        )
        return

    content = env_py.read_text()
    import_line = f"from modules.{module_folder}.models import {model_name}  # noqa"

    if import_line in content:
        typer.secho(f"  ✓  Model already registered in {env_py}", fg=typer.colors.YELLOW)
        return

    # Insert after the last existing "from modules." import, or before "target_metadata"
    insert_marker = "target_metadata"
    if insert_marker in content:
        content = content.replace(
            insert_marker,
            f"{import_line}\n{insert_marker}",
            1,
        )
        env_py.write_text(content)
        typer.secho(f"  ✓  Registered model in {env_py}", fg=typer.colors.GREEN)
    else:
        typer.secho(
            f"  ⚠  Could not auto-register model in {env_py}. "
            f"Please add manually:\n     {import_line}",
            fg=typer.colors.YELLOW,
        )
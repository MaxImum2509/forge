#!/usr/bin/env python3
"""Scripts index — SQLite database for FRV project scripts.

This module provides a CLI tool to manage a SQLite database that indexes
all scripts in the FRV project. It supports initializing the database schema
and executing arbitrary SQL queries with Rich-formatted output.

Commands:
    init: Create the database schema (idempotent).
    exec: Execute a SQL query and display results.

Example:
    >>> poetry run scripts-index init
    >>> poetry run scripts-index exec "SELECT * FROM scripts"
"""

import sqlite3
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="scripts-index",
    help="Manage the FRV scripts index (SQLite database).",
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)

DB_PATH = Path("scripts/scripts.db")

_CREATE_SCRIPTS = """
CREATE TABLE IF NOT EXISTS scripts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    path         TEXT NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    description  TEXT NOT NULL,
    usage        TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
)
"""

_CREATE_SOFTWARE = """
CREATE TABLE IF NOT EXISTS software (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
"""

_CREATE_TAGS = """
CREATE TABLE IF NOT EXISTS tags (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL UNIQUE
)
"""

_CREATE_SCRIPT_SOFTWARE = """
CREATE TABLE IF NOT EXISTS script_software (
    script_id   INTEGER REFERENCES scripts(id)  ON DELETE CASCADE,
    software_id INTEGER REFERENCES software(id) ON DELETE CASCADE,
    PRIMARY KEY (script_id, software_id)
)
"""

_CREATE_SCRIPT_TAGS = """
CREATE TABLE IF NOT EXISTS script_tags (
    script_id INTEGER REFERENCES scripts(id) ON DELETE CASCADE,
    tag_id    INTEGER REFERENCES tags(id)    ON DELETE CASCADE,
    PRIMARY KEY (script_id, tag_id)
)
"""

_DDL_STATEMENTS = [
    _CREATE_SCRIPTS,
    _CREATE_SOFTWARE,
    _CREATE_TAGS,
    _CREATE_SCRIPT_SOFTWARE,
    _CREATE_SCRIPT_TAGS,
]


def _resolve_db(db_option: Path | None) -> Path:
    """Resolve the database path, using the default if not overridden.

    Args:
        db_option: Path provided via --db option, or None.

    Returns:
        Path: Resolved database path.
    """
    return db_option if db_option is not None else DB_PATH


@app.command()
def init(
    db: Annotated[
        Path | None,
        typer.Option("--db", help="Path to the SQLite database file."),
    ] = None,
) -> None:
    """Initialize the scripts index database (idempotent).

    Creates the database file and all required tables if they do not already
    exist. Safe to run multiple times without data loss.

    Args:
        db: Override path to the SQLite database file.
    """
    db_path = _resolve_db(db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            for statement in _DDL_STATEMENTS:
                conn.execute(statement)
            conn.commit()
        console.print(f"[green]Database initialized:[/green] {db_path}")
    except sqlite3.Error as exc:
        err_console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command(name="exec")
def exec_sql(
    sql: Annotated[str, typer.Argument(help="SQL statement to execute.")],
    db: Annotated[
        Path | None,
        typer.Option("--db", help="Path to the SQLite database file."),
    ] = None,
) -> None:
    """Execute a SQL statement against the scripts index database.

    For SELECT queries, results are displayed as a Rich table.
    For INSERT/UPDATE/DELETE, the number of affected rows is shown.
    For DDL statements (CREATE/DROP), a confirmation message is shown.

    Args:
        sql: The SQL statement to execute.
        db: Override path to the SQLite database file.

    Raises:
        SystemExit: With code 1 on SQL errors.
    """
    db_path = _resolve_db(db)
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute(sql)
            conn.commit()
    except sqlite3.Error as exc:
        err_console.print(f"[red]SQL error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    sql_upper = sql.strip().upper()

    if sql_upper.startswith("SELECT"):
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        if not columns:
            console.print("[yellow]No results.[/yellow]")
            return
        table = Table(*columns, show_header=True, header_style="bold cyan")
        for row in rows:
            table.add_row(*[str(v) if v is not None else "" for v in row])
        console.print(table)
    elif any(sql_upper.startswith(kw) for kw in ("INSERT", "UPDATE", "DELETE")):
        console.print(f"[green]{cursor.rowcount} row(s) affected.[/green]")
    else:
        console.print("[green]Statement executed successfully.[/green]")


def main_entry() -> None:
    """Entry point for the scripts-index CLI.

    Delegates to the Typer application.
    """
    app()

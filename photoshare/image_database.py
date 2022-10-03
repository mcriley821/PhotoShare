import sqlite3
import click

from os.path import exists
from flask import g, current_app


def get_database():
    if "database" not in g:
        g.database = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.database.row_factory = sqlite3.Row
    return g.database


def close_database(error=None):
    db = g.pop("database", None)
    if db is not None:
        db.close()


def init_database():
    db = get_database()

    with current_app.open_resource("schema.sql", 'r') as f:
        db.executescript(f.read())


@click.command("init-database", help="initialize the images database")
def init_database_command():
    if exists(current_app.config["DATABASE"]):
        click.echo("Cowardly refusing to reinitialize database...")
        return

    init_database()
    click.echo("Successfully initialized database")


def init_app(app):
    app.teardown_appcontext(close_database)
    app.cli.add_command(init_database_command)


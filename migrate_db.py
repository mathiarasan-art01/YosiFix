"""Lightweight, idempotent schema upgrades.

``db.create_all()`` creates new tables but never adds columns to existing ones. This
adds the columns introduced by newer versions of YosiFix. It uses SQLAlchemy's
inspector so it works on SQLite (local) and PostgreSQL (production) alike.
"""
import logging

from sqlalchemy import inspect, text

logger = logging.getLogger("yosifix.migrate")

# table -> [(column, DDL type + default)]
COLUMN_UPGRADES = {
    "users": [
        ("google_id", "VARCHAR(100)"),
        ("avatar_url", "VARCHAR(255)"),
        ("preferred_language", "VARCHAR(5) DEFAULT 'en'"),
    ],
    "ideas": [
        ("status", "VARCHAR(30) DEFAULT 'draft'"),
        ("selected_mutation_id", "VARCHAR(100)"),
    ],
    "idea_versions": [
        ("actor", "VARCHAR(20) DEFAULT 'user'"),
        ("stage", "VARCHAR(40) DEFAULT 'idea'"),
        ("snapshot", "JSON"),
    ],
}


def upgrade_db(engine=None):
    """Add any missing columns. Safe to run on every start."""
    if engine is None:
        from extensions import db
        engine = db.engine

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    added = []
    with engine.begin() as conn:
        for table, columns in COLUMN_UPGRADES.items():
            if table not in existing_tables:
                continue
            present = {c["name"] for c in inspector.get_columns(table)}
            for name, ddl in columns:
                if name not in present:
                    conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {name} {ddl}'))
                    added.append(f"{table}.{name}")
    if added:
        logger.info("Schema upgraded: added %s", ", ".join(added))
    return added


if __name__ == "__main__":
    from app import create_app

    application = create_app()
    with application.app_context():
        print("Added columns:", upgrade_db() or "none (schema already current)")

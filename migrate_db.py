# migrate_db.py
"""Automatic schema migration utility to ensure all columns exist in the database."""

import sqlite3
import os


def upgrade_db(db_path=None):
    if not db_path:
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "instance", "yosifix.db"))

    if not os.path.exists(db_path):
        print(f"Database at {db_path} does not exist yet. It will be created on first start.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_results';")
    if not cursor.fetchone():
        print("Table analysis_results does not exist yet.")
        conn.close()
        return

    cursor.execute("PRAGMA table_info(analysis_results);")
    existing_cols = {row[1] for row in cursor.fetchall()}

    new_cols = [
        ("normalized_idea", "TEXT DEFAULT ''"),
        ("problem", "TEXT DEFAULT ''"),
        ("target_users", "JSON DEFAULT '[]'"),
        ("keywords", "JSON DEFAULT '[]'"),
        ("landscape", "JSON DEFAULT '{}'"),
        ("evidence", "JSON DEFAULT '{}'"),
        ("novelty", "JSON DEFAULT '{}'"),
        ("mutations", "JSON DEFAULT '[]'"),
        ("selected_mutation_id", "VARCHAR(100) DEFAULT ''"),
        ("selected_mutation_detail", "JSON DEFAULT '{}'"),
        ("reality_check", "JSON DEFAULT '{}'"),
        ("failures", "JSON DEFAULT '{}'"),
        ("judge_attack", "JSON DEFAULT '{}'"),
        ("blueprint", "JSON DEFAULT '{}'"),
        ("completed_stages", "JSON DEFAULT '[]'"),
        ("current_stage", "VARCHAR(50) DEFAULT 'initialized'"),
    ]

    for col_name, col_def in new_cols:
        if col_name not in existing_cols:
            print(f"Adding column '{col_name}' to analysis_results...")
            cursor.execute(f"ALTER TABLE analysis_results ADD COLUMN {col_name} {col_def};")

    # Migrate users table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(users);")
        user_cols = {row[1] for row in cursor.fetchall()}
        user_new_cols = [
            ("google_id", "VARCHAR(100) DEFAULT NULL"),
            ("avatar_url", "VARCHAR(255) DEFAULT NULL"),
        ]
        for col_name, col_def in user_new_cols:
            if col_name not in user_cols:
                print(f"Adding column '{col_name}' to users...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def};")

    conn.commit()
    conn.close()
    print("Database schema verified and upgraded.")


if __name__ == "__main__":
    upgrade_db()

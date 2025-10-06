#!/usr/bin/env python3
"""Backfills billing/plan columns on the legacy `users` table.

The production SQLite database was originally created with only the core
authentication columns (`email`, `name`, `created_at`, `api_token`). The
current SQLAlchemy model (`backend/models.py`) expects additional plan,
Stripe, and billing fields. This script makes the live database compatible by
adding the missing columns and indexes in-place.

Usage
-----

    python3 scripts/migrate_add_user_plan_columns.py --db lucy.sqlite3

By default the script creates a timestamped `.bak` copy of the database before
mutating it. Pass `--no-backup` to skip that safeguard. The script is idempotent;
re-running it will detect existing columns/indexes and leave them as-is.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sqlite3
from pathlib import Path
from shutil import copy2
from typing import Iterable, Mapping

DEFAULT_DB_PATH = Path("lucy.sqlite3")

COLUMN_DEFINITIONS = (
    ("plan", "TEXT NOT NULL DEFAULT 'trial'"),
    ("plan_started_at", "TEXT"),
    ("plan_metadata", "TEXT"),
    ("stripe_customer_id", "TEXT"),
    ("stripe_subscription_id", "TEXT"),
    ("billing_name", "TEXT"),
    ("billing_company", "TEXT"),
    ("billing_address_line1", "TEXT"),
    ("billing_address_line2", "TEXT"),
    ("billing_postal_code", "TEXT"),
    ("billing_city", "TEXT"),
    ("billing_region", "TEXT"),
    ("billing_country", "TEXT"),
    ("billing_tax_id", "TEXT"),
)

INDEX_DEFINITIONS = (
    (
        "ix_users_plan",
        "CREATE INDEX IF NOT EXISTS {name} ON users(plan)",
    ),
    (
        "ix_users_billing_country",
        "CREATE INDEX IF NOT EXISTS {name} ON users(billing_country)",
    ),
    (
        "ux_users_stripe_customer_id",
        "CREATE UNIQUE INDEX IF NOT EXISTS {name} ON users(stripe_customer_id) "
        "WHERE stripe_customer_id IS NOT NULL",
    ),
    (
        "ux_users_stripe_subscription_id",
        "CREATE UNIQUE INDEX IF NOT EXISTS {name} ON users(stripe_subscription_id) "
        "WHERE stripe_subscription_id IS NOT NULL",
    ),
)

DEFAULT_PLAN_METADATA = '{"tier":"free","ai_credits":0}'


def _iso_now() -> str:
    """Return a timezone-aware ISO8601 string with a trailing Z."""
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.isolation_level = None  # autocommit off; we will manage transactions
    return conn


def _existing_columns(conn: sqlite3.Connection) -> Mapping[str, int]:
    rows = conn.execute("PRAGMA table_info(users)").fetchall()
    return {row[1]: row[0] for row in rows}


def _existing_indexes(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("PRAGMA index_list('users')").fetchall()
    return {row[1] for row in rows}


def _ensure_columns(conn: sqlite3.Connection, *, dry_run: bool) -> list[str]:
    existing = _existing_columns(conn)
    applied: list[str] = []

    for name, ddl in COLUMN_DEFINITIONS:
        if name in existing:
            continue
        applied.append(name)
        if dry_run:
            continue
        conn.execute("BEGIN")
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {name} {ddl}")
            conn.execute("COMMIT")
        except Exception:  # pragma: no cover - surface the error and rollback
            conn.execute("ROLLBACK")
            raise

    if dry_run:
        return applied

    # Backfill defaults for rows that pre-date the columns.
    conn.execute(
        "UPDATE users SET plan = COALESCE(plan, 'trial') WHERE plan IS NULL"
    )
    conn.execute(
        "UPDATE users SET plan_started_at = COALESCE(plan_started_at, created_at, ?)"
        " WHERE plan_started_at IS NULL",
        (_iso_now(),),
    )
    conn.execute(
        "UPDATE users SET plan_metadata = COALESCE(plan_metadata, ?)"
        " WHERE plan_metadata IS NULL OR trim(plan_metadata) = ''",
        (DEFAULT_PLAN_METADATA,),
    )

    return applied


def _ensure_indexes(conn: sqlite3.Connection, *, dry_run: bool) -> list[str]:
    existing = _existing_indexes(conn)
    applied: list[str] = []
    for name, template in INDEX_DEFINITIONS:
        if name in existing:
            continue
        applied.append(name)
        if dry_run:
            continue
        conn.execute(template.format(name=name))
    return applied


def _make_backup(path: Path) -> Path:
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_suffix(path.suffix + f".{timestamp}.bak")
    copy2(path, backup_path)
    return backup_path


def migrate(path: Path, *, dry_run: bool, create_backup: bool) -> None:
    if not path.exists():
        raise FileNotFoundError(f"SQLite database not found: {path}")

    backup_path: Path | None = None
    if create_backup and not dry_run:
        backup_path = _make_backup(path)
        print(f"Backup created: {backup_path}")

    with _connect(path) as conn:
        columns_added = _ensure_columns(conn, dry_run=dry_run)
        indexes_added = _ensure_indexes(conn, dry_run=dry_run)

    if dry_run:
        print("Dry run complete. Pending changes:")
        if columns_added:
            print(f"  Columns → {', '.join(columns_added)}")
        if indexes_added:
            print(f"  Indexes → {', '.join(indexes_added)}")
        if not columns_added and not indexes_added:
            print("  No schema changes required.")
        return

    if columns_added:
        print(f"Columns added: {', '.join(columns_added)}")
    else:
        print("All required columns already present.")

    if indexes_added:
        print(f"Indexes added: {', '.join(indexes_added)}")
    else:
        print("All required indexes already present.")

    if backup_path is not None:
        print("Backup retained at:", backup_path)



def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to the SQLite database (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect the database and report pending changes without applying them.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip the automatic .bak copy (not recommended).",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    migrate(
        args.db,
        dry_run=args.dry_run,
        create_backup=not args.no_backup,
    )

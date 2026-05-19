"""
init_db.py — One-shot script to create database tables.

Runs once at startup, before the API workers boot.
This is the simplest version of a "migration": apply the schema, then exit.
"""

from app.main import create_app, db


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()
    print("✅ Database tables created (or already existed).")


if __name__ == "__main__":
    main()


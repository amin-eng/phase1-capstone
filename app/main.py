"""
Phase 1 Capstone — Flask REST API with PostgreSQL.

Three endpoints (same as before, now backed by a real database):
  GET  /health   -> liveness probe
  GET  /users    -> list all users
  POST /users    -> create a new user
"""

import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


# SQLAlchemy lives at module level but stays uninitialised until create_app()
# is called. This pattern is called "deferred initialisation".
db = SQLAlchemy()


class User(db.Model):
    """
    The User table. SQLAlchemy reads this class and creates the table for us.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self) -> dict:
        """Turn a User row into a JSON-friendly dict."""
        return {"id": self.id, "name": self.name, "email": self.email}


def create_app(database_uri: str | None = None) -> Flask:
    """
    App factory. Builds a fresh Flask app.

    The database_uri argument lets tests pass in an in-memory SQLite URL
    while production reads from the DATABASE_URL environment variable.
    """
    app = Flask(__name__)

    # Configuration. Order of precedence:
    #   1. Argument passed to create_app() (used by tests)
    #   2. DATABASE_URL env var (used in Docker Compose and production)
    #   3. Fallback to in-memory SQLite (so the app still boots in weird cases)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        database_uri
        or os.environ.get("DATABASE_URL")
        or "sqlite:///:memory:"
    )
    # This setting suppresses a warning and saves memory. Always set it to False.
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Bind the SQLAlchemy instance to this app.
    db.init_app(app)


    # ------------------ Routes ------------------

    @app.route("/health", methods=["GET"])
    def health():
        """Liveness probe. Returns 200 OK if the app is running."""
        return jsonify({"status": "ok"}), 200

    @app.route("/users", methods=["GET"])
    def list_users():
        """Return all users from the database."""
        users = User.query.all()
        return jsonify([u.to_dict() for u in users]), 200

    @app.route("/users", methods=["POST"])
    def create_user():
        """Create a new user from JSON body: {"name": "...", "email": "..."}"""
        data = request.get_json(silent=True)

        if not data or "name" not in data or "email" not in data:
            return jsonify({"error": "name and email are required"}), 400

        # Reject duplicate emails up front (cleaner error than DB constraint).
        if User.query.filter_by(email=data["email"]).first() is not None:
            return jsonify({"error": "email already exists"}), 409

        user = User(name=data["name"], email=data["email"])
        db.session.add(user)
        db.session.commit()

        return jsonify(user.to_dict()), 201

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

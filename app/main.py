"""
Phase 1 Capstone — Flask REST API.

Three endpoints:
  GET  /health   -> liveness probe
  GET  /users    -> list all users
  POST /users    -> create a new user

Users are kept in memory for now. We'll move to PostgreSQL in Step 8.
"""

from flask import Flask, jsonify, request


def create_app() -> Flask:
    """
    App factory. Returns a fresh Flask app with isolated state.
    Tests use this to get a clean app per test.
    """
    app = Flask(__name__)

    # State lives inside the factory so each app instance has its own.
    users: list[dict] = []
    counter = {"next_id": 1}  # dict so we can mutate it inside closures

    @app.route("/health", methods=["GET"])
    def health():
        """Liveness probe. Returns 200 OK if the app is running."""
        return jsonify({"status": "ok"}), 200

    @app.route("/users", methods=["GET"])
    def list_users():
        """Return the full list of users."""
        return jsonify(users), 200

    @app.route("/users", methods=["POST"])
    def create_user():
        """Create a new user from JSON body: {"name": "...", "email": "..."}"""
        data = request.get_json(silent=True)

        if not data or "name" not in data or "email" not in data:
            return jsonify({"error": "name and email are required"}), 400

        new_user = {
            "id": counter["next_id"],
            "name": data["name"],
            "email": data["email"],
        }
        users.append(new_user)
        counter["next_id"] += 1

        return jsonify(new_user), 201

    return app


if __name__ == "__main__":
    # When run directly, build one app and serve it.
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

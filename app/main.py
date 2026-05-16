"""
Phase 1 Capstone — Flask REST API.

Three endpoints:
  GET  /health   -> liveness probe
  GET  /users    -> list all users
  POST /users    -> create a new user

Users are kept in memory for now. We'll move to PostgreSQL in Step 8.
"""

from flask import Flask, jsonify, request

# Create the Flask application object.
app = Flask(__name__)

# In-memory "database". A list of dicts.
users = []
# A simple ID counter so each user gets a unique id.
next_id = 1


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
    global next_id

    # Parse JSON body. If it's missing or malformed, Flask gives us None.
    data = request.get_json(silent=True)

    # Validate input.
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "name and email are required"}), 400

    # Build the user record.
    new_user = {
        "id": next_id,
        "name": data["name"],
        "email": data["email"],
    }
    users.append(new_user)
    next_id += 1

    # 201 Created is the conventional status code for "I made a new resource".
    return jsonify(new_user), 201


if __name__ == "__main__":
    # host="0.0.0.0" so the app is reachable from outside the container later.
    # debug=True gives nice error pages; we'll turn it off in production.
    app.run(host="0.0.0.0", port=5000, debug=True)

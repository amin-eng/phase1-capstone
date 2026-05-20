"""
Unit tests for the Flask API.

Run with:    pytest -v
"""

import pytest
from app.main import create_app


# ----------------------------------------------------------------------
# Fixture: gives every test a brand-new app + test client.
# ----------------------------------------------------------------------
@pytest.fixture
def client():
    """Build a fresh app with an in-memory SQLite DB, create tables, yield client."""
    from app.main import db
    app = create_app(database_uri="sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
    with app.test_client() as test_client:
        yield test_client

# ----------------------------------------------------------------------
# /health
# ----------------------------------------------------------------------
def test_health_returns_200_and_ok(client):
    """GET /health should return 200 with {'status': 'ok'}."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


# ----------------------------------------------------------------------
# GET /users
# ----------------------------------------------------------------------
def test_get_users_is_empty_on_startup(client):
    """A fresh app should have no users."""
    response = client.get("/users")

    assert response.status_code == 200
    assert response.get_json() == []


# ----------------------------------------------------------------------
# POST /users
# ----------------------------------------------------------------------
def test_post_users_creates_user(client):
    """POST /users with valid data should return 201 and the new user."""
    payload = {"name": "Alice", "email": "alice@example.com"}
    response = client.post("/users", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] == 1
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"


def test_post_users_then_get_lists_the_user(client):
    """After POST, GET should return the new user in the list."""
    client.post("/users", json={"name": "Bob", "email": "bob@example.com"})

    response = client.get("/users")

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["name"] == "Bob"


def test_post_users_missing_email_returns_400(client):
    """Missing required field should return 400 Bad Request."""
    response = client.post("/users", json={"name": "Charlie"})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_post_users_no_body_returns_400(client):
    """No JSON body at all should also return 400."""
    response = client.post("/users")

    assert response.status_code == 400
    assert "error" in response.get_json()


# ----------------------------------------------------------------------
# Isolation check — proves the fixture really gives a fresh app per test.
# ----------------------------------------------------------------------
def test_users_are_isolated_between_tests(client):
    """
    If isolation works, this test sees an empty list — even though the
    earlier test created Bob. The fixture must have built a fresh app.
    """
    response = client.get("/users")
    assert response.get_json() == []


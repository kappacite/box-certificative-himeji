def test_route_register_success(client):
    """Test POST /api/auth/register success path."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert "user" in json_data["data"]
    assert json_data["data"]["user"]["username"] == "user1"
    assert "password_hash" not in json_data["data"]["user"]  # Sensitive info hidden


def test_route_register_validation_error(client):
    """Test POST /api/auth/register validation error (missing fields)."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "user1"
            # email and password missing
        },
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert json_data["code"] == "BAD_REQUEST"


def test_route_login_success(client):
    """Test POST /api/auth/login success path."""
    # Register first
    client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        },
    )

    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "user2@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert "token" in json_data["data"]
    assert json_data["data"]["user"]["username"] == "user2"


def test_route_login_unauthorized(client):
    """Test POST /api/auth/login failure path (invalid credentials)."""
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert json_data["code"] == "UNAUTHORIZED"

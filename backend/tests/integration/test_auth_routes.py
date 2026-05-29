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


def test_route_logout_and_revocation(client):
    """Test POST /api/auth/logout blacklists the token and prevents further usage."""
    # 1. Register and login
    client.post(
        "/api/auth/register",
        json={
            "username": "logoutuser",
            "email": "logoutuser@example.com",
            "password": "password123",
        },
    )
    res_login = client.post(
        "/api/auth/login",
        json={"email": "logoutuser@example.com", "password": "password123"},
    )
    token = res_login.get_json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test accessing protected route works before logout
    res_places_before = client.get("/api/places", headers=headers)
    assert res_places_before.status_code == 200

    # 3. Logout
    res_logout = client.post("/api/auth/logout", headers=headers)
    assert res_logout.status_code == 200
    assert res_logout.get_json()["data"]["message"] == "Logged out successfully"

    # 4. Test accessing protected route fails after logout (401)
    res_places_after = client.get("/api/places", headers=headers)
    assert res_places_after.status_code == 401
    assert res_places_after.get_json()["code"] == "UNAUTHORIZED"


def test_route_me_success(client):
    """Test GET /api/auth/me success path."""
    # 1. Register and login
    client.post(
        "/api/auth/register",
        json={
            "username": "meuser",
            "email": "meuser@example.com",
            "password": "password123",
        },
    )
    res_login = client.post(
        "/api/auth/login",
        json={"email": "meuser@example.com", "password": "password123"},
    )
    token = res_login.get_json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Call /api/auth/me
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["user"]["username"] == "meuser"
    assert json_data["data"]["user"]["email"] == "meuser@example.com"
    assert "password_hash" not in json_data["data"]["user"]


def test_route_me_unauthorized(client):
    """Test GET /api/auth/me when unauthenticated."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.get_json()["status"] == "error"

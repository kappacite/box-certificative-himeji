import pytest
from services.auth_service import AuthService


class MockResponse:
    def __init__(self, json_data):
        self.json_data = json_data

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass


@pytest.fixture
def mock_geocoding(monkeypatch):
    """Fixture to mock geocoding for place generation."""

    def mock_get(url, *args, **kwargs):
        query = kwargs.get("params", {}).get("q", "")
        if "Paris" in query:
            return MockResponse([{"lat": "48.8566", "lon": "2.3522"}])
        elif "Lyon" in query:
            return MockResponse([{"lat": "45.7640", "lon": "4.8357"}])
        return MockResponse([])

    monkeypatch.setattr("requests.get", mock_get)


@pytest.fixture
def auth_headers(app):
    """Fixture to create user and return Auth header."""
    with app.app_context():
        auth_service = AuthService()
        user = auth_service.register("touruser", "touruser@example.com", "password123")
        token = auth_service.generate_token(user.id)
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(app):
    """Fixture to create second user and return Auth header."""
    with app.app_context():
        auth_service = AuthService()
        user = auth_service.register(
            "touruser2", "touruser2@example.com", "password123"
        )
        token = auth_service.generate_token(user.id)
        return {"Authorization": f"Bearer {token}"}


def test_create_and_share_tour(client, auth_headers, mock_geocoding):
    """Test generating a tour, checking distance, and sharing publicly."""
    # 1. Create two places
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})

    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]

    # 2. Generate optimized tour
    res_tour = client.post(
        "/api/tours",
        headers=auth_headers,
        json={"name": "French Tour", "place_ids": [p1_id, p2_id]},
    )

    assert res_tour.status_code == 201
    tour_data = res_tour.get_json()["data"]["tour"]
    assert tour_data["name"] == "French Tour"
    assert tour_data["visibility"] == "private"
    assert tour_data["total_distance"] > 0.0
    assert len(tour_data["places"]) == 2

    tour_id = tour_data["id"]
    share_token = tour_data["share_token"]

    # 3. Verify public access is denied while private
    res_shared_denied = client.get(f"/api/tours/shared/{share_token}")
    assert res_shared_denied.status_code == 404

    # 4. Make tour public
    res_share_patch = client.patch(
        f"/api/tours/{tour_id}/share",
        headers=auth_headers,
        json={"visibility": "public"},
    )
    assert res_share_patch.status_code == 200
    assert res_share_patch.get_json()["data"]["tour"]["visibility"] == "public"

    # 5. Verify public access works now (no auth header needed)
    res_shared_ok = client.get(f"/api/tours/shared/{share_token}")
    assert res_shared_ok.status_code == 200
    assert res_shared_ok.get_json()["data"]["tour"]["name"] == "French Tour"


def test_create_tour_validation_too_few_places(client, auth_headers, mock_geocoding):
    """Test tour generation fails with fewer than 2 places."""
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    p1_id = res_p1.get_json()["data"]["place"]["id"]

    response = client.post(
        "/api/tours",
        headers=auth_headers,
        json={"name": "Short Tour", "place_ids": [p1_id]},
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert "At least 2 places" in json_data["message"]


def test_tour_creation_with_public_and_private_places(
    client, auth_headers, other_auth_headers, mock_geocoding
):
    """Test tour creation with other user's public and private places."""
    # User 1 creates one public place and one private place
    res_pub = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "public"},
    )
    res_priv = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Lyon", "visibility": "private"},
    )
    pub_place_id = res_pub.get_json()["data"]["place"]["id"]
    priv_place_id = res_priv.get_json()["data"]["place"]["id"]

    # User 2 creates their own place
    res_own = client.post(
        "/api/places", headers=other_auth_headers, json={"name": "Paris"}
    )
    own_place_id = res_own.get_json()["data"]["place"]["id"]

    # User 2 tries to create a tour with their own place + User 1's public place (should work)
    res_tour_ok = client.post(
        "/api/tours",
        headers=other_auth_headers,
        json={
            "name": "Mixed Tour",
            "place_ids": [own_place_id, pub_place_id],
            "visibility": "public",
        },
    )
    assert res_tour_ok.status_code == 201
    tour_data = res_tour_ok.get_json()["data"]["tour"]
    assert tour_data["visibility"] == "public"
    tour_id = tour_data["id"]

    # User 2 tries to create a tour with their own place + User 1's private place
    # (should be Forbidden)
    res_tour_forbidden = client.post(
        "/api/tours",
        headers=other_auth_headers,
        json={"name": "Forbidden Tour", "place_ids": [own_place_id, priv_place_id]},
    )
    assert res_tour_forbidden.status_code == 403

    # Retrieve all public tours (no headers needed)
    res_public_list = client.get("/api/tours/public")
    assert res_public_list.status_code == 200
    tours = res_public_list.get_json()["data"]["tours"]
    assert any(t["id"] == tour_id for t in tours)


def test_tour_visibility_toggling(client, auth_headers, mock_geocoding):
    """Test toggling tour sharing visibility."""
    # 1. Create two places and a tour
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})
    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]

    res_tour = client.post(
        "/api/tours",
        headers=auth_headers,
        json={"name": "French Tour", "place_ids": [p1_id, p2_id]},
    )
    tour_id = res_tour.get_json()["data"]["tour"]["id"]

    # 2. Make it public (explicitly passing visibility)
    res_patch1 = client.patch(
        f"/api/tours/{tour_id}/share",
        headers=auth_headers,
        json={"visibility": "public"},
    )
    assert res_patch1.status_code == 200
    assert res_patch1.get_json()["data"]["tour"]["visibility"] == "public"

    # 3. Toggle back to private (making request on public tour with visibility = private)
    res_patch2 = client.patch(
        f"/api/tours/{tour_id}/share",
        headers=auth_headers,
        json={"visibility": "private"},
    )
    assert res_patch2.status_code == 200
    assert res_patch2.get_json()["data"]["tour"]["visibility"] == "private"

    # 4. Make public again (toggling by sending empty payload)
    res_patch3 = client.patch(
        f"/api/tours/{tour_id}/share",
        headers=auth_headers,
        json={},
    )
    assert res_patch3.status_code == 200
    assert res_patch3.get_json()["data"]["tour"]["visibility"] == "public"

    # 5. Toggle back to private (by sending empty payload)
    res_patch4 = client.patch(
        f"/api/tours/{tour_id}/share",
        headers=auth_headers,
        json={},
    )
    assert res_patch4.status_code == 200
    assert res_patch4.get_json()["data"]["tour"]["visibility"] == "private"

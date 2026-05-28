import pytest
from services.auth_service import AuthService


class MockResponse:
    """Mock HTTP Response for Nominatim Geocoding API."""

    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass


@pytest.fixture
def mock_geocoding(monkeypatch):
    """Fixture to mock geocoding API calls during place creation."""

    def mock_get(self, url, *args, **kwargs):
        # Check if we are querying Nominatim
        if "nominatim" in url:
            query = kwargs.get("params", {}).get("q", "")
            if "Paris" in query:
                return MockResponse([{"lat": "48.8566", "lon": "2.3522"}])
            elif "Lyon" in query:
                return MockResponse([{"lat": "45.7640", "lon": "4.8357"}])
            else:
                return MockResponse([])  # No results found
        return MockResponse([], 404)

    monkeypatch.setattr("requests.Session.get", mock_get)


@pytest.fixture
def auth_headers(app):
    """Fixture to create a test user and return Authorization headers."""
    with app.app_context():
        auth_service = AuthService()
        user = auth_service.register(
            "placeuser", "placeuser@example.com", "password123"
        )
        token = auth_service.generate_token(user.id)
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_auth_headers(app):
    """Fixture to create another user to test unauthorized/forbidden actions."""
    with app.app_context():
        auth_service = AuthService()
        user = auth_service.register(
            "otheruser", "otheruser@example.com", "password123"
        )
        token = auth_service.generate_token(user.id)
        return {"Authorization": f"Bearer {token}"}


def test_create_place_with_geocoding(client, auth_headers, mock_geocoding):
    """Test creating a place by name, triggering geocoding search."""
    response = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["status"] == "success"
    place = json_data["data"]["place"]
    assert place["name"] == "Paris"
    assert place["latitude"] == 48.8566
    assert place["longitude"] == 2.3522


def test_create_place_validation_error(client, auth_headers, mock_geocoding):
    """Test geocoding failure when name cannot be resolved."""
    response = client.post(
        "/api/places", headers=auth_headers, json={"name": "UnknownCityXYZ"}
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert "Could not resolve coordinates" in json_data["message"]


def test_get_places(client, auth_headers, mock_geocoding):
    """Test listing user's places."""
    # Create one place first
    client.post("/api/places", headers=auth_headers, json={"name": "Paris"})

    response = client.get("/api/places", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert len(json_data["data"]["places"]) == 1
    assert json_data["data"]["places"][0]["name"] == "Paris"


def test_get_place_forbidden(client, auth_headers, other_auth_headers, mock_geocoding):
    """Test that a user cannot access another user's place."""
    # User 1 creates place
    res = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    place_id = res.get_json()["data"]["place"]["id"]

    # User 2 tries to fetch it
    response = client.get(f"/api/places/{place_id}", headers=other_auth_headers)
    assert response.status_code == 403
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert json_data["code"] == "FORBIDDEN"


def test_create_and_get_public_places(
    client, auth_headers, other_auth_headers, mock_geocoding
):
    """Test creating a public place and fetching it, even by other users."""
    # Create a public place
    response = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "public"},
    )
    assert response.status_code == 201
    place = response.get_json()["data"]["place"]
    assert place["visibility"] == "public"
    place_id = place["id"]

    # Retrieve all public places (no headers needed)
    response_public = client.get("/api/places/public")
    assert response_public.status_code == 200
    places = response_public.get_json()["data"]["places"]
    assert any(p["id"] == place_id for p in places)

    # Retrieve the specific public place with other user's headers (should be accessible)
    response_other = client.get(f"/api/places/{place_id}", headers=other_auth_headers)
    assert response_other.status_code == 200
    assert response_other.get_json()["data"]["place"]["name"] == "Paris"

    # Other user tries to update the place (should be Forbidden)
    response_update = client.put(
        f"/api/places/{place_id}", headers=other_auth_headers, json={"name": "Lyon"}
    )
    assert response_update.status_code == 403

    # Other user tries to delete the place (should be Forbidden)
    response_delete = client.delete(
        f"/api/places/{place_id}", headers=other_auth_headers
    )
    assert response_delete.status_code == 403

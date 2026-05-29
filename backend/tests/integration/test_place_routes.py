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


def test_create_place_rejects_partial_coordinates(client, auth_headers):
    """Test place creation rejects latitude without longitude."""
    response = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "latitude": 48.8566},
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["status"] == "error"
    assert "Latitude and longitude must be provided together" in json_data["message"]


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


def test_get_place_public_no_auth(client, auth_headers, mock_geocoding):
    """Test fetching a public place without authentication (public access)."""
    # 1. Create a public place using authentication
    res = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "public"},
    )
    place_id = res.get_json()["data"]["place"]["id"]

    # 2. Fetch the place without authorization headers
    response = client.get(f"/api/places/{place_id}")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["place"]["name"] == "Paris"
    assert json_data["data"]["place"]["visibility"] == "public"


def test_get_place_private_no_auth(client, auth_headers, mock_geocoding):
    """Test fetching a private place without authentication fails."""
    # 1. Create a private place using authentication
    res = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "private"},
    )
    place_id = res.get_json()["data"]["place"]["id"]

    # 2. Fetch the place without authorization headers (should return 401)
    response = client.get(f"/api/places/{place_id}")
    assert response.status_code == 401


def test_patch_place_partial(client, auth_headers, mock_geocoding):
    """Test PATCH endpoint with partial updates."""
    # 1. Create a private place
    res = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "private"},
    )
    place_id = res.get_json()["data"]["place"]["id"]

    # 2. Update visibility to public only
    res_patch_vis = client.patch(
        f"/api/places/{place_id}",
        headers=auth_headers,
        json={"visibility": "public"},
    )
    assert res_patch_vis.status_code == 200
    place_vis = res_patch_vis.get_json()["data"]["place"]
    assert place_vis["name"] == "Paris"
    assert place_vis["visibility"] == "public"

    # 3. Update coordinates only
    res_patch_coords = client.patch(
        f"/api/places/{place_id}",
        headers=auth_headers,
        json={"latitude": 45.0, "longitude": 5.0},
    )
    assert res_patch_coords.status_code == 200
    place_coords = res_patch_coords.get_json()["data"]["place"]
    assert place_coords["latitude"] == 45.0
    assert place_coords["longitude"] == 5.0
    assert place_coords["name"] == "Paris"

    # 4. Update name only (which triggers geocoding to Lyon)
    res_patch_name = client.patch(
        f"/api/places/{place_id}",
        headers=auth_headers,
        json={"name": "Lyon"},
    )
    assert res_patch_name.status_code == 200
    place_name = res_patch_name.get_json()["data"]["place"]
    assert place_name["name"] == "Lyon"
    assert place_name["latitude"] == 45.7640
    assert place_name["longitude"] == 4.8357


def test_patch_place_rejects_partial_coordinates(
    client, auth_headers, mock_geocoding
):
    """Test PATCH endpoint rejects a single coordinate field."""
    res = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "private"},
    )
    place_id = res.get_json()["data"]["place"]["id"]

    res_patch = client.patch(
        f"/api/places/{place_id}",
        headers=auth_headers,
        json={"latitude": 45.0},
    )

    assert res_patch.status_code == 400
    json_data = res_patch.get_json()
    assert json_data["status"] == "error"
    assert "Latitude and longitude must be provided together" in json_data["message"]


def test_geocode_and_search_preview(client, mock_geocoding):
    """Test geocoding preview routes (GET /search and POST /geocode)."""
    # 1. Test search with GET
    res_search = client.get("/api/places/search?q=Paris")
    assert res_search.status_code == 200
    data_search = res_search.get_json()["data"]
    assert data_search["latitude"] == 48.8566
    assert data_search["longitude"] == 2.3522

    # 2. Test search with invalid query
    res_search_fail = client.get("/api/places/search?q=")
    assert res_search_fail.status_code == 400

    # 3. Test geocode with POST
    res_geocode = client.post("/api/places/geocode", json={"name": "Lyon"})
    assert res_geocode.status_code == 200
    data_geocode = res_geocode.get_json()["data"]
    assert data_geocode["latitude"] == 45.7640
    assert data_geocode["longitude"] == 4.8357

    # 4. Test geocode with missing name
    res_geocode_fail = client.post("/api/places/geocode", json={})
    assert res_geocode_fail.status_code == 400


def test_places_search_and_pagination(client, auth_headers, mock_geocoding):
    """Test searching and paginating user places and public places."""
    # 1. Create multiple places
    client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "public"},
    )
    client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Lyon", "visibility": "private"},
    )
    client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "visibility": "private"},
    )

    # 2. Filter user's places by q=Paris
    res_q = client.get("/api/places?q=Paris", headers=auth_headers)
    assert res_q.status_code == 200
    places_q = res_q.get_json()["data"]["places"]
    assert len(places_q) == 2
    assert all("Paris" in p["name"] for p in places_q)

    # 3. Paginate user's places: page=1, limit=1
    res_page1 = client.get("/api/places?page=1&limit=1", headers=auth_headers)
    assert res_page1.status_code == 200
    places_p1 = res_page1.get_json()["data"]["places"]
    assert len(places_p1) == 1

    # 4. Paginate public places: limit=1
    res_pub_page = client.get("/api/places/public?limit=1")
    assert res_pub_page.status_code == 200
    places_pub = res_pub_page.get_json()["data"]["places"]
    assert len(places_pub) <= 1

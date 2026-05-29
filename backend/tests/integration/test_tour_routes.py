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

    def mock_get(self, url, *args, **kwargs):
        if "nominatim" in url or "search" in url:
            query = kwargs.get("params", {}).get("q", "")
            if "Paris" in query:
                return MockResponse([{"lat": "48.8566", "lon": "2.3522"}])
            elif "Lyon" in query:
                return MockResponse([{"lat": "45.7640", "lon": "4.8357"}])
        return MockResponse([])

    monkeypatch.setattr("requests.Session.get", mock_get)


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
    assert len(tour_data["places"]) == 3
    assert tour_data["places"][0]["id"] == tour_data["places"][-1]["id"]

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


def test_create_tour_with_locked_positions(client, auth_headers, mock_geocoding):
    """Test generating a tour with some steps locked at specific positions."""
    # 1. Create three places
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris 1"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})
    res_p3 = client.post("/api/places", headers=auth_headers, json={"name": "Paris 2"})

    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]
    p3_id = res_p3.get_json()["data"]["place"]["id"]

    # 2. Generate optimized tour with p2_id (Lyon) locked at position 1 (second place)
    # and p3_id (Paris 2) locked at position 0 (start place)
    res_tour = client.post(
        "/api/tours",
        headers=auth_headers,
        json={
            "name": "Locked Tour",
            "place_ids": [p1_id, p2_id, p3_id],
            "locked_positions": {str(p3_id): 0, str(p2_id): 1},
            "max_distance": 0.0,
        },
    )

    assert res_tour.status_code == 201
    tour_data = res_tour.get_json()["data"]["tour"]
    # For a 3-place tour with return-to-start, the places list has length 4
    assert len(tour_data["places"]) == 4
    # Paris 2 (p3_id) must be at position 0 (and at the end due to closed loop)
    assert tour_data["places"][0]["id"] == p3_id
    assert tour_data["places"][-1]["id"] == p3_id
    # Lyon (p2_id) must be at position 1
    assert tour_data["places"][1]["id"] == p2_id
    # The place at position 2 must be Paris 1 (p1_id)
    assert tour_data["places"][2]["id"] == p1_id

    # Also check that the locked status is returned in the places
    assert tour_data["places"][0]["locked"] is True
    assert tour_data["places"][1]["locked"] is True
    assert tour_data["places"][2]["locked"] is False


def test_preview_tour(client, auth_headers, mock_geocoding):
    """Test generating a tour preview without saving it to database."""
    # 1. Create two places
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})

    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]

    # 2. Preview tour
    res_preview = client.post(
        "/api/tours/preview",
        headers=auth_headers,
        json={"place_ids": [p1_id, p2_id]},
    )

    assert res_preview.status_code == 200
    preview_data = res_preview.get_json()["data"]["tour"]
    assert preview_data["name"] == "Preview"
    assert preview_data["id"] is None
    assert preview_data["total_distance"] > 0.0
    assert len(preview_data["places"]) == 3

    # 3. Check that it was not persisted
    res_tours_list = client.get("/api/tours", headers=auth_headers)
    assert res_tours_list.status_code == 200
    tours = res_tours_list.get_json()["data"]["tours"]
    assert len(tours) == 0


def test_recalculate_tour(client, auth_headers, mock_geocoding):
    """Test recalculating a tour's distance and order after place coordinates change."""
    # 1. Create two places and a tour
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})
    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]

    res_tour = client.post(
        "/api/tours",
        headers=auth_headers,
        json={"name": "Tour to Recalculate", "place_ids": [p1_id, p2_id]},
    )
    tour_id = res_tour.get_json()["data"]["tour"]["id"]
    old_distance = res_tour.get_json()["data"]["tour"]["total_distance"]

    # 2. Modify one place's coordinates via PATCH (Paris to new latitude)
    client.patch(
        f"/api/places/{p1_id}",
        headers=auth_headers,
        json={"latitude": 10.0, "longitude": 20.0},
    )

    # 3. Recalculate tour
    res_recalc = client.post(
        f"/api/tours/{tour_id}/recalculate",
        headers=auth_headers,
    )
    assert res_recalc.status_code == 200
    new_distance = res_recalc.get_json()["data"]["tour"]["total_distance"]
    assert new_distance != old_distance





def test_tours_search_and_pagination(client, auth_headers, mock_geocoding):
    """Test search query and pagination on tours endpoints."""
    # 1. Create two places
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})
    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]

    # 2. Create multiple tours
    client.post(
        "/api/tours",
        headers=auth_headers,
        json={
            "name": "France Route 1",
            "place_ids": [p1_id, p2_id],
            "visibility": "public",
        },
    )
    client.post(
        "/api/tours",
        headers=auth_headers,
        json={
            "name": "France Route 2",
            "place_ids": [p1_id, p2_id],
            "visibility": "private",
        },
    )

    # 3. Filter by search query q=Route 1
    res_q = client.get("/api/tours?q=Route 1", headers=auth_headers)
    assert res_q.status_code == 200
    tours_q = res_q.get_json()["data"]["tours"]
    assert len(tours_q) == 1
    assert tours_q[0]["name"] == "France Route 1"

    # 4. Paginate public list: page=1, limit=1
    res_pub = client.get("/api/tours/public?page=1&limit=1")
    assert res_pub.status_code == 200
    tours_pub = res_pub.get_json()["data"]["tours"]
    assert len(tours_pub) == 1


def test_optimize_tour_route(client, auth_headers):
    """Test POST /api/tours/optimize endpoint."""
    # 1. Create three places
    res_p1 = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    )
    res_p2 = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Lyon", "latitude": 45.7640, "longitude": 4.8357},
    )
    res_p3 = client.post(
        "/api/places",
        headers=auth_headers,
        json={"name": "Marseille", "latitude": 43.2964, "longitude": 5.3697},
    )

    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]
    p3_id = res_p3.get_json()["data"]["place"]["id"]

    # 2. Call optimize endpoint locking Marseille (p3_id) at position 1
    res_opt = client.post(
        "/api/tours/optimize",
        headers=auth_headers,
        json={"place_ids": [p1_id, p2_id, p3_id], "locked_positions": {str(p3_id): 1}},
    )

    assert res_opt.status_code == 200
    res_data = res_opt.get_json()["data"]
    assert "places" in res_data
    assert "total_distance" in res_data
    places = res_data["places"]
    assert len(places) == 4
    # Marseille (p3_id) must be at index 1
    assert places[1]["id"] == p3_id


def test_create_tour_with_hotels_grouping(client, auth_headers, mock_geocoding):
    """Test generating a tour where nearby places are grouped into a hotel."""
    # 1. Create three places: Paris, Lyon, Paris 2
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})
    res_p3 = client.post("/api/places", headers=auth_headers, json={"name": "Paris 2"})

    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]
    p3_id = res_p3.get_json()["data"]["place"]["id"]

    # 2. Create tour with default max_distance=100.0 km
    res_tour = client.post(
        "/api/tours",
        headers=auth_headers,
        json={
            "name": "Grouping Tour",
            "place_ids": [p1_id, p2_id, p3_id],
        },
    )

    assert res_tour.status_code == 201
    tour_data = res_tour.get_json()["data"]["tour"]

    # Places sequence should be:
    # Paris 1 (H1) -> Paris 2 -> Paris 1 -> Lyon (H2) -> Paris 1 (H1)
    places = tour_data["places"]
    assert len(places) == 5
    assert places[0]["id"] == p1_id
    assert places[0]["is_hotel"] is True
    assert places[1]["id"] == p3_id
    assert places[1]["is_hotel"] is False
    assert places[2]["id"] == p1_id
    assert places[2]["is_hotel"] is True
    assert places[3]["id"] == p2_id
    assert places[3]["is_hotel"] is True
    assert places[4]["id"] == p1_id
    assert places[4]["is_hotel"] is True


def test_delete_place_cascade(client, auth_headers, mock_geocoding):
    """Test that when a place included in a tour is deleted:
    1. The tour doesn't crash on fetch
    2. The deleted place is removed/ignored in the retrieved tour
    """
    # 1. Create two places
    res_p1 = client.post("/api/places", headers=auth_headers, json={"name": "Paris"})
    res_p2 = client.post("/api/places", headers=auth_headers, json={"name": "Lyon"})
    p1_id = res_p1.get_json()["data"]["place"]["id"]
    p2_id = res_p2.get_json()["data"]["place"]["id"]

    # 2. Create a tour with them
    res_tour = client.post(
        "/api/tours",
        headers=auth_headers,
        json={"name": "Cascade Test Tour", "place_ids": [p1_id, p2_id]},
    )
    assert res_tour.status_code == 201
    tour_id = res_tour.get_json()["data"]["tour"]["id"]

    # 3. Delete one of the places (Lyon)
    res_delete_place = client.delete(
        f"/api/places/{p2_id}",
        headers=auth_headers
    )
    assert res_delete_place.status_code == 204

    # 4. Fetch the tour and verify it does not crash, and the place is gone
    res_get_tour = client.get(
        f"/api/tours/{tour_id}",
        headers=auth_headers
    )
    assert res_get_tour.status_code == 200
    tour_data = res_get_tour.get_json()["data"]["tour"]
    # Check that Lyon is no longer in the places list of the tour
    remaining_place_ids = [p["id"] for p in tour_data["places"]]
    assert p2_id not in remaining_place_ids


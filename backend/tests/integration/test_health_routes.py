def test_health_check(client):
    """Test the static health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["message"] == "Service is healthy"


def test_health_ready_success(client):
    """Test the ready health check endpoint verifying database connection."""
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["message"] == "Database and service are ready"

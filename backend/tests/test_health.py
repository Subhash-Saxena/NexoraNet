from fastapi import status
from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient) -> None:
    """
    Test GET /api/health endpoint.
    Requirement:
    Response status: HTTP 200
    Body contains:
    {
      "status": "ok",
      "service": "NexoraNet API"
    }
    """
    response = client.get("/api/health")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "NexoraNet API"


def test_root_endpoint(client: TestClient) -> None:
    """Test GET / root metadata endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == "NexoraNet API"
    assert data["status"] == "online"

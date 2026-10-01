import pytest
from fastapi import status
from fastapi.testclient import TestClient

V1_MODULE_STUBS = [
    "/api/v1/learning",
    "/api/v1/packet-analysis",
    "/api/v1/simulator",
    "/api/v1/detection",
    "/api/v1/soc",
    "/api/v1/progress",
]


@pytest.mark.parametrize("endpoint", V1_MODULE_STUBS)
def test_v1_module_stubs(client: TestClient, endpoint: str) -> None:
    """Verify planned v1 endpoints respond with valid module metadata."""
    response = client.get(endpoint)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "module" in data
    assert data["status"] == "planned"
    assert "planned_phase" in data
    assert isinstance(data["capabilities"], list)

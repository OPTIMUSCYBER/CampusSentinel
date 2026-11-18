from fastapi.testclient import TestClient

def test_create_lab(client: TestClient):
    response = client.post(
        "/api/v1/labs",
        json={"name": "Science Lab", "location": "Room 200"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Science Lab"
    assert "id" in data

def test_duplicate_lab_rejected(client: TestClient, sample_lab):
    response = client.post(
        "/api/v1/labs",
        json={"name": "Main Lab", "location": "Somewhere else"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_list_labs(client: TestClient, sample_lab):
    response = client.get("/api/v1/labs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(lab["name"] == "Main Lab" for lab in data)

from fastapi.testclient import TestClient

def test_enroll_new_device(client: TestClient, sample_lab, db):
    response = client.post(
        "/api/v1/devices/enroll",
        json={
            "device_uid": "DEVICE-1234",
            "hostname": "test-pc",
            "mac_address": "00:1A:2B:3C:4D:5E",
            "lab_id": sample_lab.id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["device_uid"] == "DEVICE-1234"
    assert data["status"] == "active"
    assert data["lab_id"] == sample_lab.id
    # TestClient uses 127.0.0.1 or testclient by default
    assert data["ip_address"] == "testclient"

def test_enroll_existing_device(client: TestClient):
    # First enrollment
    client.post(
        "/api/v1/devices/enroll",
        json={"device_uid": "DEVICE-5555", "hostname": "old-name"}
    )
    
    # Re-enrollment with new data
    response = client.post(
        "/api/v1/devices/enroll",
        json={"device_uid": "DEVICE-5555", "hostname": "new-name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hostname"] == "new-name"
    assert data["ip_address"] == "testclient"

def test_list_devices(client: TestClient, sample_lab):
    client.post("/api/v1/devices/enroll", json={"device_uid": "DEV-1", "lab_id": sample_lab.id})
    client.post("/api/v1/devices/enroll", json={"device_uid": "DEV-2"})
    
    # List all
    res = client.get("/api/v1/devices")
    assert res.status_code == 200
    assert len(res.json()) >= 2
    
    # Filter by lab_id
    res_lab = client.get(f"/api/v1/devices?lab_id={sample_lab.id}")
    assert res_lab.status_code == 200
    for d in res_lab.json():
        assert d["lab_id"] == sample_lab.id

def test_get_device_by_uid(client: TestClient):
    client.post("/api/v1/devices/enroll", json={"device_uid": "DEV-TARGET"})
    
    res = client.get("/api/v1/devices/DEV-TARGET")
    assert res.status_code == 200
    assert res.json()["device_uid"] == "DEV-TARGET"
    
def test_get_device_not_found(client: TestClient):
    res = client.get("/api/v1/devices/BOGUS-UID")
    assert res.status_code == 404

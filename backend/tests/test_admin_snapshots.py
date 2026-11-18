from fastapi.testclient import TestClient

def test_admin_get_latest_snapshot(client: TestClient, sample_lab):
    client.post("/api/v1/devices/enroll", json={"device_uid": "SNAP-TEST"})
    
    # Send a heartbeat to create a snapshot
    client.post(
        "/api/v1/agent/heartbeat",
        headers={"x-device-uid": "SNAP-TEST"},
        json={"processes": ["test.exe"], "applications": ["Test App"]}
    )
    
    res = client.get("/api/v1/admin/devices/SNAP-TEST/snapshot")
    assert res.status_code == 200
    data = res.json()
    assert "test.exe" in data["processes"]
    assert "Test App" in data["applications"]

def test_admin_get_snapshot_not_found(client: TestClient):
    client.post("/api/v1/devices/enroll", json={"device_uid": "SNAP-EMPTY"})
    
    res = client.get("/api/v1/admin/devices/SNAP-EMPTY/snapshot")
    assert res.status_code == 404

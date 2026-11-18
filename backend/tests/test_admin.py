from fastapi.testclient import TestClient

def test_admin_list_devices(client: TestClient, sample_lab):
    # Enroll a device
    client.post(
        "/api/v1/devices/enroll",
        json={"device_uid": "DEV-ADMIN-1", "lab_id": sample_lab.id}
    )
    
    # Admin list should include joined lab_name
    res = client.get("/api/v1/admin/devices")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    
    device = next(d for d in data if d["device_uid"] == "DEV-ADMIN-1")
    assert device["lab_name"] == sample_lab.name

def test_admin_device_history(client: TestClient):
    # Enroll (creates 'enrolled' event)
    client.post("/api/v1/devices/enroll", json={"device_uid": "DEV-HIST"})
    # Re-enroll (creates 're_seen' event)
    client.post("/api/v1/devices/enroll", json={"device_uid": "DEV-HIST"})
    
    res = client.get("/api/v1/admin/devices/DEV-HIST/history")
    assert res.status_code == 200
    events = res.json()
    
    assert len(events) == 2
    # Newest first
    assert events[0]["event_type"] == "re_seen"
    assert events[1]["event_type"] == "enrolled"

def test_admin_device_history_not_found(client: TestClient):
    res = client.get("/api/v1/admin/devices/BOGUS/history")
    assert res.status_code == 404

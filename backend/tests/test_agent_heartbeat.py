from fastapi.testclient import TestClient

def test_agent_heartbeat_success(client: TestClient, sample_lab):
    # Enroll a device
    client.post(
        "/api/v1/devices/enroll",
        json={"device_uid": "AGENT-TEST-1", "lab_id": sample_lab.id}
    )

    # Send heartbeat
    res = client.post(
        "/api/v1/agent/heartbeat",
        headers={"x-device-uid": "AGENT-TEST-1"},
        json={"processes": ["chrome.exe", "code.exe"], "applications": ["Google Chrome"]}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_agent_heartbeat_unauthorized(client: TestClient):
    res = client.post(
        "/api/v1/agent/heartbeat",
        headers={"x-device-uid": "UNKNOWN-DEV"},
        json={"processes": [], "applications": []}
    )
    assert res.status_code == 401

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.device import Device
from app.models.device_snapshot import DeviceSnapshot
from app.schemas.device_snapshot import DeviceSnapshotCreate

router = APIRouter()

@router.post("/heartbeat", response_model=dict)
def agent_heartbeat(
    payload: DeviceSnapshotCreate,
    x_device_uid: str = Header(..., description="Device UID for authentication"),
    db: Session = Depends(get_db)
):
    # Authenticate device
    device = db.query(Device).filter(Device.device_uid == x_device_uid).first()
    if not device:
        raise HTTPException(status_code=401, detail="Unauthorized or unknown device UID")

    # Update last seen
    device.last_seen_at = datetime.now(timezone.utc)
    
    # Store snapshot
    snapshot = DeviceSnapshot(
        device=device,
        processes=payload.processes,
        applications=payload.applications,
        captured_at=datetime.now(timezone.utc)
    )
    db.add(snapshot)
    db.commit()
    
    return {"status": "ok", "message": "Heartbeat accepted"}

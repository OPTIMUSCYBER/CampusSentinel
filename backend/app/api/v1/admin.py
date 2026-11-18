from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.db.session import get_db
from app.models.device import Device, DeviceStatus
from app.models.device_event import DeviceEvent
from app.schemas.device import DeviceAdminRead, DeviceEventRead

router = APIRouter()

@router.get("/devices", response_model=List[DeviceAdminRead])
def get_all_devices(
    lab_id: Optional[int] = None,
    status: Optional[DeviceStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(Device).options(joinedload(Device.lab))
    
    if lab_id is not None:
        query = query.filter(Device.lab_id == lab_id)
    if status is not None:
        query = query.filter(Device.status == status)
        
    devices = query.offset(skip).limit(limit).all()
    
    # Map the lab name explicitly since the schema expects lab_name instead of a full lab object
    result = []
    for d in devices:
        # Pydantic from_attributes works best if we construct a dict or rely on alias/property.
        # It's easiest to just build the dict here.
        d_dict = d.__dict__.copy()
        d_dict["lab_name"] = d.lab.name if d.lab else None
        result.append(d_dict)
        
    return result

@router.get("/devices/{device_uid}/history", response_model=List[DeviceEventRead])
def get_device_history(device_uid: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uid == device_uid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    events = db.query(DeviceEvent).filter(DeviceEvent.device_id == device.id).order_by(DeviceEvent.occurred_at.desc()).all()
    return events

from app.models.device_snapshot import DeviceSnapshot
from app.schemas.device_snapshot import DeviceSnapshotRead

@router.get("/devices/{device_uid}/snapshot", response_model=DeviceSnapshotRead)
def get_device_latest_snapshot(device_uid: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uid == device_uid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    snapshot = db.query(DeviceSnapshot).filter(DeviceSnapshot.device_id == device.id).order_by(DeviceSnapshot.captured_at.desc()).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshots found for device")
        
    return snapshot

@router.get("/devices/{device_uid}/snapshots", response_model=List[DeviceSnapshotRead])
def get_device_snapshots(device_uid: str, limit: int = 10, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uid == device_uid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    snapshots = db.query(DeviceSnapshot).filter(DeviceSnapshot.device_id == device.id).order_by(DeviceSnapshot.captured_at.desc()).limit(limit).all()
    return snapshots

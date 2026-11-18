from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.device import Device, DeviceStatus
from app.models.device_event import DeviceEvent, EventType
from app.schemas.device import DeviceEnroll, DeviceRead

router = APIRouter()

@router.post("/enroll", response_model=DeviceRead)
def enroll_device(payload: DeviceEnroll, request: Request, db: Session = Depends(get_db)):
    # Note: For reverse-proxy deployment, we will need to read X-Forwarded-For
    client_ip = request.client.host if request.client else None
    
    device = db.query(Device).filter(Device.device_uid == payload.device_uid).first()
    
    if device:
        # Update existing device
        device.hostname = payload.hostname or device.hostname
        device.mac_address = payload.mac_address or device.mac_address
        device.ip_address = client_ip
        device.lab_id = payload.lab_id if payload.lab_id is not None else device.lab_id
        device.last_seen_at = datetime.now(timezone.utc)
        
        event = DeviceEvent(device=device, event_type=EventType.re_seen, detail="Device checked in")
        db.add(event)
    else:
        # Create new device
        device = Device(
            device_uid=payload.device_uid,
            hostname=payload.hostname,
            mac_address=payload.mac_address,
            ip_address=client_ip,
            lab_id=payload.lab_id,
            last_seen_at=datetime.now(timezone.utc)
        )
        db.add(device)
        
        event = DeviceEvent(device=device, event_type=EventType.enrolled, detail="Device enrolled")
        db.add(event)
    
    db.commit()
    db.refresh(device)
    return device

@router.get("", response_model=List[DeviceRead])
def list_devices(
    lab_id: Optional[int] = None,
    status: Optional[DeviceStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(Device)
    
    if lab_id is not None:
        query = query.filter(Device.lab_id == lab_id)
    if status is not None:
        query = query.filter(Device.status == status)
        
    devices = query.offset(skip).limit(limit).all()
    return devices

@router.get("/{device_uid}", response_model=DeviceRead)
def get_device(device_uid: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uid == device_uid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

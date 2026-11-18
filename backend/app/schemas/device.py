from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional
from app.models.device import DeviceStatus
from app.models.device_event import EventType

class DeviceBase(BaseModel):
    hostname: str | None = None
    mac_address: str | None = None
    lab_id: int | None = None

class DeviceEnroll(DeviceBase):
    device_uid: str = Field(..., description="Stable client-supplied unique identifier")

class DeviceRead(DeviceBase):
    id: int
    device_uid: str
    ip_address: str | None = None
    status: DeviceStatus
    enrolled_at: datetime
    last_seen_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)

class DeviceAdminRead(DeviceRead):
    lab_name: str | None = None

class DeviceEventRead(BaseModel):
    id: int
    event_type: EventType
    detail: str | None = None
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)

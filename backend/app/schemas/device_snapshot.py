from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class DeviceSnapshotBase(BaseModel):
    processes: List[str] = []
    applications: List[str] = []

class DeviceSnapshotCreate(DeviceSnapshotBase):
    pass

class DeviceSnapshotRead(DeviceSnapshotBase):
    id: int
    captured_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

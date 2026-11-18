from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LabBase(BaseModel):
    name: str
    location: str | None = None

class LabCreate(LabBase):
    pass

class LabRead(LabBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

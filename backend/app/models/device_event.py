from datetime import datetime, timezone
import enum
from sqlalchemy import String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class EventType(str, enum.Enum):
    enrolled = "enrolled"
    re_seen = "re_seen"
    status_changed = "status_changed"

class DeviceEvent(Base):
    __tablename__ = "device_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    event_type: Mapped[EventType] = mapped_column(Enum(EventType))
    detail: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    device: Mapped["Device"] = relationship("Device", back_populates="events")

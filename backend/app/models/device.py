from datetime import datetime, timezone
import enum
from sqlalchemy import String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class DeviceStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    quarantined = "quarantined"

from typing import List

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_uid: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hostname: Mapped[str | None] = mapped_column(String(255))
    mac_address: Mapped[str | None] = mapped_column(String(100))
    ip_address: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[DeviceStatus] = mapped_column(Enum(DeviceStatus), default=DeviceStatus.active)
    lab_id: Mapped[int | None] = mapped_column(ForeignKey("labs.id"))
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    lab: Mapped["Lab"] = relationship("Lab", back_populates="devices")
    events: Mapped[List["DeviceEvent"]] = relationship("DeviceEvent", back_populates="device", cascade="all, delete-orphan")
    snapshots: Mapped[List["DeviceSnapshot"]] = relationship("DeviceSnapshot", back_populates="device", cascade="all, delete-orphan")

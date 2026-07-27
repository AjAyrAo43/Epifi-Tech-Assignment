from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    url = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    checks = relationship("Check", back_populates="url_rel", cascade="all, delete-orphan")


class Check(Base):
    __tablename__ = "checks"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False, index=True)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    is_up = Column(Boolean, nullable=False)
    checked_at = Column(DateTime, default=utc_now, index=True)

    url_rel = relationship("URL", back_populates="checks")

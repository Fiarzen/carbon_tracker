from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from db_base import Base

class EmissionResult(Base):
    __tablename__ = "emission_results"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100))
    subcategory = Column(String(100))
    activity = Column(String(100))
    co2_kg = Column(Float)
    details = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
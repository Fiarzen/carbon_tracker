from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, func
from datetime import datetime
from src.db_base import Base

class DBResult(Base):
    __tablename__ = "emission_results"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    subcategory = Column(String)
    activity = Column(String)
    co2_kg = Column(Float)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
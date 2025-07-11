"""
Database Module for Carbon Tracking Application

This module handles interaction with the PostgreSQL database using SQLAlchemy ORM.
It stores emission calculation results for tracking and analysis.
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, JSON, DateTime, text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from dotenv import load_dotenv
from src.models import DBResult
from src.db_base import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DATABASE")

DATABASE_URL = (
    f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class EmissionResult(Base):
    """SQLAlchemy model for an emission result"""
    __tablename__ = "emission_results"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String, nullable=True)
    subcategory = Column(String, nullable=True)
    activity = Column(String, nullable=True)
    co2_kg = Column(Float, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def insert_emission_result(result):
    """
    Insert a DBResult instance (from calculator.py) into the database
    """

    if not isinstance(result, DBResult):
        raise TypeError("Expected a DBResult instance")

    session = SessionLocal()
    try:
        record = EmissionResult(
            category=result.category,
            subcategory=result.subcategory,
            activity=result.activity,
            co2_kg=result.co2_kg,
            details=result.details
        )
        session.add(record)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def create_database_if_not_exists():
    # Read connection params from env vars (make sure these are set)
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = os.getenv("PG_PORT", "5432")
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASSWORD = os.getenv("PG_PASSWORD", "")
    PG_DATABASE = os.getenv("PG_DATABASE", "carbon_tracker")

    # Connect to the default 'postgres' database to check/create target database
    conn = psycopg2.connect(
        dbname='postgres',
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (PG_DATABASE,))
    exists = cursor.fetchone()

    if not exists:
        print(f"Database '{PG_DATABASE}' does not exist. Creating...")
        cursor.execute(f'CREATE DATABASE "{PG_DATABASE}";')
        print(f"Database '{PG_DATABASE}' created.")
    else:
        print(f"Database '{PG_DATABASE}' already exists.")

    cursor.close()
    conn.close() 

def create_tables():
    Base.metadata.create_all(bind=engine)

def save_emission_result(result):  # also import here
    session = SessionLocal()
    try:
        db_result = EmissionResult(
            category=result.category,
            subcategory=result.subcategory,
            activity=result.activity,
            co2_kg=result.co2_kg,
            details=result.details,
        )
        session.add(db_result)
        session.commit()
        session.refresh(db_result)
        return db_result.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))  # wrap query in text()
            print("✅ Connected to database:", result.scalar())
    except Exception as e:
        print("❌ Database connection failed:", e)
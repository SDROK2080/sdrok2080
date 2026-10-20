import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False)  # 'scrape', 'api', 'upload', 'url', 'sample'
    source_url = Column(String(1024), nullable=True)
    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(1024), nullable=False)
    cleaned_file_path = Column(String(1024), nullable=True)
    
    total_rows = Column(Integer, default=0)
    total_columns = Column(Integer, default=0)
    columns_json = Column(Text, default="[]")
    
    country = Column(String(100), default="Nepal")
    is_official_source = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Audit & operation history
    history = relationship("ProcessingHistory", back_populates="dataset", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="dataset", cascade="all, delete-orphan")

class ProcessingHistory(Base):
    __tablename__ = "processing_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    operation = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    dataset = relationship("Dataset", back_populates="history")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    sections_json = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    findings_json = Column(Text, nullable=True)
    recommendations_json = Column(Text, nullable=True)
    charts_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    dataset = relationship("Dataset", back_populates="reports")

class SavedAPI(Base):
    __tablename__ = "saved_apis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    endpoint_url = Column(String(1024), nullable=False)
    method = Column(String(10), default="GET")
    params_json = Column(Text, default="{}")
    headers_json = Column(Text, default="{}")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

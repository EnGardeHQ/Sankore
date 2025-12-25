import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Boolean
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from src.db.base import Base

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type for PostgreSQL, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class AdTrend(Base):
    __tablename__ = "ad_trends"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    platform = Column(String, nullable=False, index=True)  # meta, tiktok, google
    format = Column(String, nullable=False)  # video, image, carousel
    industry = Column(String, nullable=False, index=True)
    trend_type = Column(String, nullable=False) # visual_style, audio, copy_angle
    trend_name = Column(String, nullable=False)
    trend_score = Column(Float, default=0.0)
    data = Column(JSON, default={})
    captured_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    industry = Column(String, nullable=False, index=True)
    objective = Column(String, nullable=False) # conversion, traffic, awareness
    avg_ctr = Column(Float)
    avg_cpc = Column(Float)
    avg_roas = Column(Float)
    period = Column(String, nullable=False) # Q1_2025, Jan_2025
    updated_at = Column(DateTime, default=datetime.utcnow)

class WinningPattern(Base):
    __tablename__ = "winning_patterns"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    pattern_type = Column(String, nullable=False, index=True) # hook, cta, color_palette, keyword
    value = Column(String, nullable=False) # e.g. "Stop scrolling", "#FF0000"
    vertical = Column(String, index=True)
    performance_score = Column(Float) # Normalized score 0-100
    confidence_level = Column(Float)
    source_count = Column(Integer, default=1)
    detected_at = Column(DateTime, default=datetime.utcnow)

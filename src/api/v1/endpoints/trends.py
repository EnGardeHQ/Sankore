from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from src.api import deps
from src.db.models.intelligence import AdTrend
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic Schemas (Move to schemas/ later if large)
class AdTrendCreate(BaseModel):
    platform: str
    format: str
    industry: str
    trend_type: str
    trend_name: str
    trend_score: float
    data: dict

class AdTrendResponse(AdTrendCreate):
    id: UUID
    captured_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AdTrendResponse])
async def read_trends(
    skip: int = 0,
    limit: int = 100,
    industry: Optional[str] = None,
    platform: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db)
):
    query = select(AdTrend).where(AdTrend.is_active == True)
    
    if industry:
        query = query.where(AdTrend.industry == industry)
    if platform:
        query = query.where(AdTrend.platform == platform)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/fetch", response_model=List[AdTrendResponse])
async def trigger_fetch_trends(
    industry: str,
    db: AsyncSession = Depends(deps.get_db)
):
    from src.services.trends.aggregator import TrendAggregator
    aggregator = TrendAggregator(db)
    result = await aggregator.fetch_and_store_trends(industry)
    return result

@router.post("/", response_model=AdTrendResponse)
async def create_trend(
    trend_in: AdTrendCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    trend = AdTrend(**trend_in.dict())
    db.add(trend)
    await db.commit()
    await db.refresh(trend)
    return trend

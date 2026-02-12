from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID
from src.api import deps
from src.db.models.intelligence import AdTrend
from pydantic import BaseModel, Field
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

class AdTrendResponse(BaseModel):
    id: UUID
    platform: str
    trend_name: str
    trend_score: float
    description: str  # Computed from data dict
    created_at: datetime  # Mapped from captured_at
    updated_at: Optional[datetime] = None  # For frontend compatibility

    # Additional fields for internal use
    format: Optional[str] = None
    industry: Optional[str] = None
    trend_type: Optional[str] = None
    data: Optional[dict] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

class PaginatedTrendsResponse(BaseModel):
    results: List[AdTrendResponse]
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None

@router.get("/", response_model=PaginatedTrendsResponse)
async def read_trends(
    skip: int = 0,
    limit: int = 100,
    industry: Optional[str] = None,
    platform: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Get paginated list of ad trends with frontend-compatible response format.

    Returns:
    - results: List of trend objects
    - count: Total number of trends matching the filters
    - next: URL for next page (not implemented yet)
    - previous: URL for previous page (not implemented yet)
    """
    # Build base query
    query = select(AdTrend).where(AdTrend.is_active == True)

    # Apply filters
    if industry:
        query = query.where(AdTrend.industry == industry)
    if platform:
        query = query.where(AdTrend.platform == platform)

    # Get total count (before pagination)
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0

    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    trends = result.scalars().all()

    # Transform to frontend-compatible format
    results = []
    for trend in trends:
        # Extract description from data dict (use a key like "description" or convert to string)
        description = ""
        if trend.data and isinstance(trend.data, dict):
            # Try to get description from data dict, or use a summary
            description = trend.data.get("description", trend.data.get("summary", ""))
            if not description:
                # Fallback: create a description from available data
                description = f"{trend.trend_type} trend in {trend.industry}"

        trend_response = AdTrendResponse(
            id=trend.id,
            platform=trend.platform,
            trend_name=trend.trend_name,
            trend_score=trend.trend_score,
            description=description,
            created_at=trend.captured_at,  # Map captured_at to created_at
            updated_at=trend.captured_at,  # Use captured_at as fallback
            format=trend.format,
            industry=trend.industry,
            trend_type=trend.trend_type,
            data=trend.data,
            is_active=trend.is_active
        )
        results.append(trend_response)

    return PaginatedTrendsResponse(
        results=results,
        count=total_count,
        next=None,  # TODO: Implement pagination URLs
        previous=None  # TODO: Implement pagination URLs
    )

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

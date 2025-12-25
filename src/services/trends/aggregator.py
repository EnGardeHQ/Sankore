from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.services.trends.base import TrendResult
from src.services.trends.providers.meta import MetaTrendProvider
from src.services.trends.providers.tiktok import TikTokTrendProvider
from src.db.models.intelligence import AdTrend
import logging

logger = logging.getLogger(__name__)

class TrendAggregator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.providers = [
            MetaTrendProvider(),
            TikTokTrendProvider()
        ]

    async def fetch_and_store_trends(self, industry: str) -> List[AdTrend]:
        """
        Fetch trends from all providers, deduplicate, and store in DB.
        """
        all_results: List[TrendResult] = []
        
        for provider in self.providers:
            try:
                results = await provider.fetch_trends(industry)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Error fetching trends from provider {provider}: {e}")
                continue

        stored_trends = []
        for res in all_results:
            # Check if exists (simple check by name/platform for now)
            # In production, use hash content or more robust ID
            query = select(AdTrend).where(
                AdTrend.platform == res.platform,
                AdTrend.trend_name == res.trend_name
            )
            existing = await self.db.execute(query)
            if existing.scalars().first():
                continue

            trend_db = AdTrend(
                platform=res.platform,
                format=res.format,
                industry=industry,
                trend_type=res.trend_type,
                trend_name=res.trend_name,
                trend_score=res.score,
                data={
                    "description": res.description, 
                    "metadata": res.metadata
                }
            )
            self.db.add(trend_db)
            stored_trends.append(trend_db)
        
        if stored_trends:
            await self.db.commit()
            for t in stored_trends:
                await self.db.refresh(t)
                
        return stored_trends

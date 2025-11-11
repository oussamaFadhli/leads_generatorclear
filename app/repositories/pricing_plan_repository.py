from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import PricingPlan
from app.repositories.base import BaseRepository

class PricingPlanRepository(BaseRepository[PricingPlan]):
    def __init__(self, db: AsyncSession):
        super().__init__(PricingPlan, db)

    async def get_by_plan_name(self, plan_name: str) -> Optional[PricingPlan]:
        result = await self.db.execute(select(self.model).filter(self.model.plan_name == plan_name))
        return result.scalars().first()

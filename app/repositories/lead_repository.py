from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Lead
from app.repositories.base import BaseRepository

class LeadRepository(BaseRepository[Lead]):
    def __init__(self, db: AsyncSession):
        super().__init__(Lead, db)

    async def get_by_competitor_name(self, competitor_name: str) -> Optional[Lead]:
        result = await self.db.execute(select(self.model).filter(self.model.competitor_name == competitor_name))
        return result.scalars().first()

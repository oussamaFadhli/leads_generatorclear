import select
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Feature
from app.repositories.base import BaseRepository

class FeatureRepository(BaseRepository[Feature]):
    def __init__(self, db: AsyncSession):
        super().__init__(Feature, db)

    async def get_by_name(self, name: str) -> Optional[Feature]:
        result = await self.db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import SaaSInfo
from app.repositories.base import BaseRepository

class SaaSInfoRepository(BaseRepository[SaaSInfo]):
    def __init__(self, db: AsyncSession):
        super().__init__(SaaSInfo, db)

    async def get_by_name(self, name: str) -> Optional[SaaSInfo]:
        result = await self.db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()

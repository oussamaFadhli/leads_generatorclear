from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import RedditComment
from app.repositories.base import BaseRepository

class RedditCommentRepository(BaseRepository[RedditComment]):
    def __init__(self, db: AsyncSession):
        super().__init__(RedditComment, db)

    async def get_by_comment_id(self, comment_id: str) -> Optional[RedditComment]:
        result = await self.db.execute(select(self.model).filter(self.model.comment_id == comment_id))
        return result.scalars().first()

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import RedditPost
from app.repositories.base import BaseRepository

class RedditPostRepository(BaseRepository[RedditPost]):
    def __init__(self, db: AsyncSession):
        super().__init__(RedditPost, db)

    async def get_by_title(self, title: str) -> Optional[RedditPost]:
        result = await self.db.execute(select(self.model).filter(self.model.title == title))
        return result.scalars().first()

    async def has_posted_to_subreddit(self, lead_id: int, generated_title: str, subreddit_name: str) -> bool:
        stmt = select(self.model.id).where(
            self.model.lead_id == lead_id,
            self.model.generated_title == generated_title,
            self.model.is_posted == True,  # noqa: E712
            self.model.subreddits.contains([subreddit_name]),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
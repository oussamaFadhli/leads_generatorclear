from typing import List, Optional
from app.core.cqrs import QueryHandler
from app.queries.reddit_post_queries import GetRedditPostByIdQuery, GetRedditPostByTitleQuery, ListRedditPostsQuery
from app.repositories import RedditPostRepository
from app.schemas.schemas import RedditPost as RedditPostSchema
from sqlalchemy.future import select

class GetRedditPostByIdQueryHandler(QueryHandler[GetRedditPostByIdQuery, Optional[RedditPostSchema]]):
    def __init__(self, reddit_post_repo: RedditPostRepository):
        self.reddit_post_repo = reddit_post_repo

    async def handle(self, query: GetRedditPostByIdQuery) -> Optional[RedditPostSchema]:
        reddit_post = await self.reddit_post_repo.get(query.reddit_post_id)
        return RedditPostSchema.model_validate(reddit_post) if reddit_post else None

class GetRedditPostByTitleQueryHandler(QueryHandler[GetRedditPostByTitleQuery, Optional[RedditPostSchema]]):
    def __init__(self, reddit_post_repo: RedditPostRepository):
        self.reddit_post_repo = reddit_post_repo

    async def handle(self, query: GetRedditPostByTitleQuery) -> Optional[RedditPostSchema]:
        reddit_post = await self.reddit_post_repo.get_by_title(query.title)
        return RedditPostSchema.model_validate(reddit_post) if reddit_post else None

class ListRedditPostsQueryHandler(QueryHandler[ListRedditPostsQuery, List[RedditPostSchema]]):
    def __init__(self, reddit_post_repo: RedditPostRepository):
        self.reddit_post_repo = reddit_post_repo

    async def handle(self, query: ListRedditPostsQuery) -> List[RedditPostSchema]:
        stmt = select(self.reddit_post_repo.model)
        if query.lead_id:
            stmt = stmt.filter(self.reddit_post_repo.model.lead_id == query.lead_id)
        
        result = await self.reddit_post_repo.db.execute(stmt.offset(query.skip).limit(query.limit))
        reddit_posts_list = result.scalars().all()
        return [RedditPostSchema.model_validate(reddit_post) for reddit_post in reddit_posts_list]

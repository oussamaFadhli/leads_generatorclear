from typing import List, Optional
from app.core.cqrs import QueryHandler
from app.queries.reddit_comment_queries import (
    GetRedditCommentByIdQuery,
    GetRedditCommentByCommentIdQuery,
    ListRedditCommentsQuery,
)
from app.repositories import RedditCommentRepository
from app.schemas.schemas import RedditComment as RedditCommentSchema
from sqlalchemy.future import select

class GetRedditCommentByIdQueryHandler(QueryHandler[GetRedditCommentByIdQuery, Optional[RedditCommentSchema]]):
    def __init__(self, reddit_comment_repo: RedditCommentRepository):
        self.reddit_comment_repo = reddit_comment_repo

    async def handle(self, query: GetRedditCommentByIdQuery) -> Optional[RedditCommentSchema]:
        comment = await self.reddit_comment_repo.get(query.reddit_comment_id)
        return RedditCommentSchema.model_validate(comment) if comment else None

class GetRedditCommentByCommentIdQueryHandler(QueryHandler[GetRedditCommentByCommentIdQuery, Optional[RedditCommentSchema]]):
    def __init__(self, reddit_comment_repo: RedditCommentRepository):
        self.reddit_comment_repo = reddit_comment_repo

    async def handle(self, query: GetRedditCommentByCommentIdQuery) -> Optional[RedditCommentSchema]:
        comment = await self.reddit_comment_repo.get_by_comment_id(query.comment_id)
        return RedditCommentSchema.model_validate(comment) if comment else None

class ListRedditCommentsQueryHandler(QueryHandler[ListRedditCommentsQuery, List[RedditCommentSchema]]):
    def __init__(self, reddit_comment_repo: RedditCommentRepository):
        self.reddit_comment_repo = reddit_comment_repo

    async def handle(self, query: ListRedditCommentsQuery) -> List[RedditCommentSchema]:
        stmt = select(self.reddit_comment_repo.model)
        if query.reddit_post_db_id:
            stmt = stmt.filter(self.reddit_comment_repo.model.reddit_post_db_id == query.reddit_post_db_id)
        
        result = await self.reddit_comment_repo.db.execute(stmt.offset(query.skip).limit(query.limit))
        comments_list = result.scalars().all()
        return [RedditCommentSchema.model_validate(comment) for comment in comments_list]

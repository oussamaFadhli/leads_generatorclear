from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Query
from app.schemas.schemas import RedditComment as RedditCommentSchema

class GetRedditCommentByIdQuery(BaseModel, Query[RedditCommentSchema]):
    reddit_comment_id: int

class GetRedditCommentByCommentIdQuery(BaseModel, Query[RedditCommentSchema]):
    comment_id: str

class ListRedditCommentsQuery(BaseModel, Query[List[RedditCommentSchema]]):
    skip: int = 0
    limit: int = 100
    reddit_post_db_id: Optional[int] = None

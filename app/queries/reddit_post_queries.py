from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Query
from app.schemas.schemas import RedditPost as RedditPostSchema

class GetRedditPostByIdQuery(BaseModel, Query[RedditPostSchema]):
    reddit_post_id: int

class GetRedditPostByTitleQuery(BaseModel, Query[RedditPostSchema]):
    title: str

class ListRedditPostsQuery(BaseModel, Query[List[RedditPostSchema]]):
    skip: int = 0
    limit: int = 100
    lead_id: Optional[int] = None

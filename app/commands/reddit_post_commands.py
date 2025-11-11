from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Command

class CreateRedditPostCommand(Command, BaseModel):
    title: str
    content: str
    score: int
    num_comments: int
    author: str
    url: str
    subreddits: List[str]
    lead_id: int

class UpdateRedditPostCommand(Command, BaseModel):
    reddit_post_id: int
    title: Optional[str] = None
    content: Optional[str] = None
    score: Optional[int] = None
    num_comments: Optional[int] = None
    author: Optional[str] = None
    url: Optional[str] = None
    subreddits: Optional[List[str]] = None
    lead_score: Optional[float] = None
    score_justification: Optional[str] = None
    generated_title: Optional[str] = None
    generated_content: Optional[str] = None
    is_posted: Optional[bool] = None
    ai_generated: Optional[bool] = None
    posted_url: Optional[str] = None

class DeleteRedditPostCommand(Command, BaseModel):
    reddit_post_id: int

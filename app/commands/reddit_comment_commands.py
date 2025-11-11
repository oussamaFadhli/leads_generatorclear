from pydantic import BaseModel
from typing import Optional
from app.core.cqrs import Command

class CreateRedditCommentCommand(Command, BaseModel):
    comment_id: str
    post_id: str
    author: str
    content: str
    score: int
    permalink: str
    reddit_post_db_id: int

class UpdateRedditCommentCommand(Command, BaseModel):
    reddit_comment_id: int
    content: Optional[str] = None
    score: Optional[int] = None
    generated_reply_content: Optional[str] = None
    is_replied: Optional[bool] = None
    ai_generated: Optional[bool] = None

class DeleteRedditCommentCommand(Command, BaseModel):
    reddit_comment_id: int

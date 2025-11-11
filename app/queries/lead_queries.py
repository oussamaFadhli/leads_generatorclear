from pydantic import BaseModel
from typing import List
from app.core.cqrs import Query
from app.schemas.schemas import Lead as LeadSchema

class GetLeadByIdQuery(BaseModel, Query[LeadSchema]):
    lead_id: int

class GetLeadByCompetitorNameQuery(BaseModel, Query[LeadSchema]):
    competitor_name: str

class ListLeadsQuery(BaseModel, Query[List[LeadSchema]]):
    skip: int = 0
    limit: int = 100

class CheckIfAlreadyPostedToSubredditQuery(BaseModel, Query[bool]):
    lead_id: int
    generated_title: str
    subreddit_name: str
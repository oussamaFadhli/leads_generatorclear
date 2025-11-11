from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Command

class CreateLeadCommand(Command, BaseModel):
    competitor_name: str
    strengths: List[str]
    weaknesses: List[str]
    related_subreddits: List[str]
    saas_info_id: int

class UpdateLeadCommand(Command, BaseModel):
    lead_id: int
    competitor_name: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    related_subreddits: Optional[List[str]] = None

class DeleteLeadCommand(Command, BaseModel):
    lead_id: int

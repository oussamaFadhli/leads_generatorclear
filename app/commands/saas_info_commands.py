from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Command

class CreateSaaSInfoCommand(Command, BaseModel):
    name: str
    one_liner: str
    target_segments: List[str]

class UpdateSaaSInfoCommand(Command, BaseModel):
    saas_info_id: int
    name: Optional[str] = None
    one_liner: Optional[str] = None
    target_segments: Optional[List[str]] = None

class DeleteSaaSInfoCommand(Command, BaseModel):
    saas_info_id: int

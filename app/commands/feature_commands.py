from pydantic import BaseModel
from typing import Optional
from app.core.cqrs import Command

class CreateFeatureCommand(Command, BaseModel):
    name: str
    description: str
    saas_info_id: int

class UpdateFeatureCommand(Command, BaseModel):
    feature_id: int
    name: Optional[str] = None
    description: Optional[str] = None

class DeleteFeatureCommand(Command, BaseModel):
    feature_id: int

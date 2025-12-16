from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.cqrs import Command


class CreateSaaSInfoCommand(Command, BaseModel):
    payload: Dict[str, Any]


class UpdateSaaSInfoCommand(Command, BaseModel):
    saas_info_id: int
    payload: Optional[Dict[str, Any]] = None


class DeleteSaaSInfoCommand(Command, BaseModel):
    saas_info_id: int

from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Command

class CreatePricingPlanCommand(Command, BaseModel):
    plan_name: str
    price: str
    features: List[str]
    link: Optional[str] = None
    saas_info_id: int

class UpdatePricingPlanCommand(Command, BaseModel):
    pricing_plan_id: int
    plan_name: Optional[str] = None
    price: Optional[str] = None
    features: Optional[List[str]] = None
    link: Optional[str] = None

class DeletePricingPlanCommand(Command, BaseModel):
    pricing_plan_id: int

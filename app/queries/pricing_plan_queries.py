from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Query
from app.schemas.schemas import PricingPlan as PricingPlanSchema

class GetPricingPlanByIdQuery(BaseModel, Query[PricingPlanSchema]):
    pricing_plan_id: int

class GetPricingPlanByPlanNameQuery(BaseModel, Query[PricingPlanSchema]):
    plan_name: str

class ListPricingPlansQuery(BaseModel, Query[List[PricingPlanSchema]]):
    skip: int = 0
    limit: int = 100
    saas_info_id: Optional[int] = None

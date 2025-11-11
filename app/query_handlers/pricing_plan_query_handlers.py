from typing import List, Optional
from app.core.cqrs import QueryHandler
from app.queries.pricing_plan_queries import GetPricingPlanByIdQuery, GetPricingPlanByPlanNameQuery, ListPricingPlansQuery
from app.repositories import PricingPlanRepository
from app.schemas.schemas import PricingPlan as PricingPlanSchema
from sqlalchemy.future import select

class GetPricingPlanByIdQueryHandler(QueryHandler[GetPricingPlanByIdQuery, Optional[PricingPlanSchema]]):
    def __init__(self, pricing_plan_repo: PricingPlanRepository):
        self.pricing_plan_repo = pricing_plan_repo

    async def handle(self, query: GetPricingPlanByIdQuery) -> Optional[PricingPlanSchema]:
        pricing_plan = await self.pricing_plan_repo.get(query.pricing_plan_id)
        return PricingPlanSchema.model_validate(pricing_plan) if pricing_plan else None

class GetPricingPlanByPlanNameQueryHandler(QueryHandler[GetPricingPlanByPlanNameQuery, Optional[PricingPlanSchema]]):
    def __init__(self, pricing_plan_repo: PricingPlanRepository):
        self.pricing_plan_repo = pricing_plan_repo

    async def handle(self, query: GetPricingPlanByPlanNameQuery) -> Optional[PricingPlanSchema]:
        pricing_plan = await self.pricing_plan_repo.get_by_plan_name(query.plan_name)
        return PricingPlanSchema.model_validate(pricing_plan) if pricing_plan else None

class ListPricingPlansQueryHandler(QueryHandler[ListPricingPlansQuery, List[PricingPlanSchema]]):
    def __init__(self, pricing_plan_repo: PricingPlanRepository):
        self.pricing_plan_repo = pricing_plan_repo

    async def handle(self, query: ListPricingPlansQuery) -> List[PricingPlanSchema]:
        stmt = select(self.pricing_plan_repo.model)
        if query.saas_info_id:
            stmt = stmt.filter(self.pricing_plan_repo.model.saas_info_id == query.saas_info_id)
        
        result = await self.pricing_plan_repo.db.execute(stmt.offset(query.skip).limit(query.limit))
        pricing_plans_list = result.scalars().all()
        return [PricingPlanSchema.model_validate(pricing_plan) for pricing_plan in pricing_plans_list]

from app.core.cqrs import CommandHandler
from app.commands.pricing_plan_commands import CreatePricingPlanCommand, UpdatePricingPlanCommand, DeletePricingPlanCommand
from app.repositories import PricingPlanRepository
from app.models.models import PricingPlan
from typing import Optional

class CreatePricingPlanCommandHandler(CommandHandler[CreatePricingPlanCommand]):
    def __init__(self, pricing_plan_repo: PricingPlanRepository):
        self.pricing_plan_repo = pricing_plan_repo

    async def handle(self, command: CreatePricingPlanCommand) -> PricingPlan:
        pricing_plan_data = command.model_dump()
        return await self.pricing_plan_repo.create(pricing_plan_data)

class UpdatePricingPlanCommandHandler(CommandHandler[UpdatePricingPlanCommand]):
    def __init__(self, pricing_plan_repo: PricingPlanRepository):
        self.pricing_plan_repo = pricing_plan_repo

    async def handle(self, command: UpdatePricingPlanCommand) -> Optional[PricingPlan]:
        pricing_plan = await self.pricing_plan_repo.get(command.pricing_plan_id)
        if not pricing_plan:
            return None
        update_data = command.model_dump(exclude_unset=True)
        return await self.pricing_plan_repo.update(pricing_plan, update_data)

class DeletePricingPlanCommandHandler(CommandHandler[DeletePricingPlanCommand]):
    def __init__(self, pricing_plan_repo: PricingPlanRepository):
        self.pricing_plan_repo = pricing_plan_repo

    async def handle(self, command: DeletePricingPlanCommand) -> bool:
        pricing_plan = await self.pricing_plan_repo.get(command.pricing_plan_id)
        if not pricing_plan:
            return False
        await self.pricing_plan_repo.delete(pricing_plan)
        return True

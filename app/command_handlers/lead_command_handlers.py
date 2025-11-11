from app.core.cqrs import CommandHandler
from app.commands.lead_commands import CreateLeadCommand, UpdateLeadCommand, DeleteLeadCommand
from app.repositories import LeadRepository
from app.models.models import Lead
from typing import Optional

class CreateLeadCommandHandler(CommandHandler[CreateLeadCommand]):
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def handle(self, command: CreateLeadCommand) -> Lead:
        lead_data = command.model_dump()
        return await self.lead_repo.create(lead_data)

class UpdateLeadCommandHandler(CommandHandler[UpdateLeadCommand]):
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def handle(self, command: UpdateLeadCommand) -> Optional[Lead]:
        lead = await self.lead_repo.get(command.lead_id)
        if not lead:
            return None
        update_data = command.model_dump(exclude_unset=True)
        return await self.lead_repo.update(lead, update_data)

class DeleteLeadCommandHandler(CommandHandler[DeleteLeadCommand]):
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def handle(self, command: DeleteLeadCommand) -> bool:
        lead = await self.lead_repo.get(command.lead_id)
        if not lead:
            return False
        await self.lead_repo.delete(lead)
        return True

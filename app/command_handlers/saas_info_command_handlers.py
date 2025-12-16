from app.core.cqrs import CommandHandler
from app.commands.saas_info_commands import CreateSaaSInfoCommand, UpdateSaaSInfoCommand, DeleteSaaSInfoCommand
from app.repositories import SaaSInfoRepository
from app.models.models import SaaSInfo
from typing import Optional

class CreateSaaSInfoCommandHandler(CommandHandler[CreateSaaSInfoCommand]):
    def __init__(self, saas_info_repo: SaaSInfoRepository):
        self.saas_info_repo = saas_info_repo

    async def handle(self, command: CreateSaaSInfoCommand) -> SaaSInfo:
        # Expect a payload dict with SaaSInfoCreate-compatible shape
        payload = command.payload if hasattr(command, "payload") else command.model_dump()
        return await self.saas_info_repo.create(payload)

class UpdateSaaSInfoCommandHandler(CommandHandler[UpdateSaaSInfoCommand]):
    def __init__(self, saas_info_repo: SaaSInfoRepository):
        self.saas_info_repo = saas_info_repo

    async def handle(self, command: UpdateSaaSInfoCommand) -> Optional[SaaSInfo]:
        saas_info = await self.saas_info_repo.get(command.saas_info_id)
        if not saas_info:
            return None
        update_data = command.payload if getattr(command, "payload", None) is not None else command.model_dump(exclude_unset=True)
        return await self.saas_info_repo.update(saas_info, update_data)

class DeleteSaaSInfoCommandHandler(CommandHandler[DeleteSaaSInfoCommand]):
    def __init__(self, saas_info_repo: SaaSInfoRepository):
        self.saas_info_repo = saas_info_repo

    async def handle(self, command: DeleteSaaSInfoCommand) -> bool:
        saas_info = await self.saas_info_repo.get(command.saas_info_id)
        if not saas_info:
            return False
        await self.saas_info_repo.delete(saas_info)
        return True

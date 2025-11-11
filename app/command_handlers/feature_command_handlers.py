from app.core.cqrs import CommandHandler
from app.commands.feature_commands import CreateFeatureCommand, UpdateFeatureCommand, DeleteFeatureCommand
from app.repositories import FeatureRepository
from app.models.models import Feature
from typing import Optional

class CreateFeatureCommandHandler(CommandHandler[CreateFeatureCommand]):
    def __init__(self, feature_repo: FeatureRepository):
        self.feature_repo = feature_repo

    async def handle(self, command: CreateFeatureCommand) -> Feature:
        feature_data = command.model_dump()
        return await self.feature_repo.create(feature_data)

class UpdateFeatureCommandHandler(CommandHandler[UpdateFeatureCommand]):
    def __init__(self, feature_repo: FeatureRepository):
        self.feature_repo = feature_repo

    async def handle(self, command: UpdateFeatureCommand) -> Optional[Feature]:
        feature = await self.feature_repo.get(command.feature_id)
        if not feature:
            return None
        update_data = command.model_dump(exclude_unset=True)
        return await self.feature_repo.update(feature, update_data)

class DeleteFeatureCommandHandler(CommandHandler[DeleteFeatureCommand]):
    def __init__(self, feature_repo: FeatureRepository):
        self.feature_repo = feature_repo

    async def handle(self, command: DeleteFeatureCommand) -> bool:
        feature = await self.feature_repo.get(command.feature_id)
        if not feature:
            return False
        await self.feature_repo.delete(feature)
        return True

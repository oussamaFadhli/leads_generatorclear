from app.core.cqrs import Command, CommandHandler, CommandBus
from app.commands.task_commands import CreateTaskCommand, UpdateTaskStatusCommand
from app.services.task_service import TaskService
from app.schemas.schemas import TaskCreate, TaskUpdate

class CreateTaskCommandHandler(CommandHandler[CreateTaskCommand]):
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def handle(self, command: CreateTaskCommand) -> None:
        task_data = TaskCreate(
            agent_id=command.agent_id,
            task_name=command.task_name,
            status=command.status,
            result_data=command.result_data
        )
        await self.task_service.create_task(task_data)

class UpdateTaskStatusCommandHandler(CommandHandler[UpdateTaskStatusCommand]):
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def handle(self, command: UpdateTaskStatusCommand) -> None:
        await self.task_service.update_task_status(
            task_id=command.task_id,
            status=command.status,
            result_data=command.result_data
        )

def register_task_command_handlers(command_bus: CommandBus, task_service: TaskService):
    command_bus.register(CreateTaskCommand, CreateTaskCommandHandler(task_service))
    command_bus.register(UpdateTaskStatusCommand, UpdateTaskStatusCommandHandler(task_service))

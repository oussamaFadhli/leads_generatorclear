from typing import Optional, List
from app.models.models import Task
from app.schemas.schemas import TaskCreate, TaskUpdate, Task as TaskSchema
from app.repositories.task_repository import TaskRepository
from app.core.websocket_manager import WebSocketManager
import json

class TaskService:
    def __init__(self, task_repository: TaskRepository, websocket_manager: WebSocketManager):
        self.task_repository = task_repository
        self.websocket_manager = websocket_manager

    async def create_task(self, task_data: TaskCreate) -> Task:
        task = await self.task_repository.create(task_data)
        await self._send_task_update_to_client(task.agent_id, task) # Assuming agent_id is the client_id
        return task

    async def get_task(self, task_id: int) -> Optional[Task]:
        return await self.task_repository.get(task_id)

    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        return await self.task_repository.get_all_tasks(skip=skip, limit=limit)

    async def update_task_status(self, task_id: int, status: str, result_data: dict = None) -> Optional[Task]:
        task = await self.task_repository.update_status(task_id, status, result_data)
        if task:
            await self._send_task_update_to_client(task.agent_id, task) # Assuming agent_id is the client_id
        return task

    async def get_tasks_by_agent_id(self, agent_id: str) -> List[Task]:
        return await self.task_repository.get_by_agent_id(agent_id)

    async def _send_task_update_to_client(self, client_id: str, task: Task):
        task_schema = TaskSchema.from_orm(task)
        message = json.dumps({"type": "task_update", "task": task_schema.dict()})
        await self.websocket_manager.broadcast_to_client(client_id, message)

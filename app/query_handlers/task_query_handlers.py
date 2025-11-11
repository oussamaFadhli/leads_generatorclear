from typing import List
from app.core.cqrs import Query, QueryHandler, QueryBus
from app.queries.task_queries import GetTaskQuery, GetAllTasksQuery, GetTasksByAgentIdQuery
from app.services.task_service import TaskService
from app.schemas.schemas import Task as TaskSchema

class GetTaskQueryHandler(QueryHandler[GetTaskQuery, TaskSchema]):
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def handle(self, query: GetTaskQuery) -> TaskSchema:
        task = await self.task_service.get_task(query.task_id)
        if not task:
            raise ValueError(f"Task with ID {query.task_id} not found.")
        return TaskSchema.from_orm(task)

class GetAllTasksQueryHandler(QueryHandler[GetAllTasksQuery, List[TaskSchema]]):
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def handle(self, query: GetAllTasksQuery) -> List[TaskSchema]:
        tasks = await self.task_service.get_all_tasks(skip=query.skip, limit=query.limit)
        return [TaskSchema.from_orm(task) for task in tasks]

class GetTasksByAgentIdQueryHandler(QueryHandler[GetTasksByAgentIdQuery, List[TaskSchema]]):
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def handle(self, query: GetTasksByAgentIdQuery) -> List[TaskSchema]:
        tasks = await self.task_service.get_tasks_by_agent_id(query.agent_id)
        return [TaskSchema.from_orm(task) for task in tasks]

def register_task_query_handlers(query_bus: QueryBus, task_service: TaskService):
    query_bus.register(GetTaskQuery, GetTaskQueryHandler(task_service))
    query_bus.register(GetAllTasksQuery, GetAllTasksQueryHandler(task_service))
    query_bus.register(GetTasksByAgentIdQuery, GetTasksByAgentIdQueryHandler(task_service))

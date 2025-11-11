from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession # Use AsyncSession
from app.repositories.base import BaseRepository
from app.models.models import Task
from app.schemas.schemas import TaskCreate, TaskUpdate
from sqlalchemy.future import select # Import select for async queries

class TaskRepository(BaseRepository[Task]): # Only pass Task model
    def __init__(self, db: AsyncSession): # Use AsyncSession
        super().__init__(Task, db)

    async def create(self, obj_in: TaskCreate) -> Task: # Override create to handle TaskCreate schema
        return await super().create(obj_in.dict())

    async def get_by_agent_id(self, agent_id: str) -> List[Task]: # Make async
        result = await self.db.execute(select(self.model).filter(self.model.agent_id == agent_id))
        return result.scalars().all()

    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]: # Make async
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_status(self, task_id: int, status: str, result_data: dict = None) -> Optional[Task]: # Make async
        task = await self.get(task_id)
        if task:
            task.status = status
            if result_data:
                task.result_data = result_data
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)
        return task

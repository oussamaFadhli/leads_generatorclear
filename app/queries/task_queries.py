from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class GetTaskQuery:
    task_id: int

@dataclass(frozen=True)
class GetAllTasksQuery:
    skip: int = 0
    limit: int = 100

@dataclass(frozen=True)
class GetTasksByAgentIdQuery:
    agent_id: str
    skip: int = 0
    limit: int = 100

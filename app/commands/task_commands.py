from dataclasses import dataclass
from typing import Optional, Dict

@dataclass(frozen=True)
class CreateTaskCommand:
    agent_id: str
    task_name: str
    status: str = "pending"
    result_data: Optional[Dict] = None

@dataclass(frozen=True)
class UpdateTaskStatusCommand:
    task_id: int
    status: str
    result_data: Optional[Dict] = None

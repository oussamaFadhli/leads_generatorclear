from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.core.dependencies import get_query_bus, get_command_bus
from app.core.cqrs import QueryBus, CommandBus
from app.schemas.schemas import Task as TaskSchema
from app.queries.task_queries import GetTaskQuery, GetAllTasksQuery, GetTasksByAgentIdQuery
from app.commands.task_commands import CreateTaskCommand, UpdateTaskStatusCommand
from app.core.websocket_manager import websocket_manager

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.get("/", response_model=List[TaskSchema])
async def get_all_tasks(
    skip: int = 0,
    limit: int = 100,
    query_bus: QueryBus = Depends(get_query_bus)
):
    query = GetAllTasksQuery(skip=skip, limit=limit)
    return await query_bus.dispatch(query)

@router.get("/{task_id}", response_model=TaskSchema)
async def get_task_by_id(
    task_id: int,
    query_bus: QueryBus = Depends(get_query_bus)
):
    try:
        query = GetTaskQuery(task_id=task_id)
        return await query_bus.dispatch(query)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/agent/{agent_id}", response_model=List[TaskSchema])
async def get_tasks_by_agent_id(
    agent_id: str,
    skip: int = 0,
    limit: int = 100,
    query_bus: QueryBus = Depends(get_query_bus)
):
    query = GetTasksByAgentIdQuery(agent_id=agent_id, skip=skip, limit=limit)
    return await query_bus.dispatch(query)

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # Keep the connection alive, or handle incoming messages if needed
            # For now, we just expect to send messages from the backend
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, client_id)

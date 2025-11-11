from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import List

from app.schemas.schemas import SaaSInfo, SaaSInfoCreate, Feature, PricingPlan
from app.core.dependencies import get_command_bus, get_query_bus
from app.core.cqrs import CommandBus, QueryBus
from app.commands.saas_info_commands import CreateSaaSInfoCommand, UpdateSaaSInfoCommand, DeleteSaaSInfoCommand
from app.queries.saas_info_queries import GetSaaSInfoByIdQuery, GetSaaSInfoByNameQuery, ListSaaSInfoQuery
from app.services.saas_scraper_service import perform_saas_scrape # Keep for now, will refactor later

router = APIRouter(
    prefix="/saas-info",
    tags=["SaaS Info"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_saas_info_endpoint( # type: ignore
    saas_info_create: SaaSInfoCreate,
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    existing_saas_info = await query_bus.dispatch(GetSaaSInfoByNameQuery(name=saas_info_create.name))
    if existing_saas_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SaaS Info with this name already exists")
    
    command = CreateSaaSInfoCommand(
        name=saas_info_create.name,
        one_liner=saas_info_create.one_liner,
        target_segments=saas_info_create.target_segments if saas_info_create.target_segments else []
    )
    created_saas_info = await command_bus.dispatch(command)
    return created_saas_info.model_dump()

@router.post("/scrape", status_code=status.HTTP_202_ACCEPTED)
async def trigger_saas_scrape_endpoint( # type: ignore
    url: str,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(perform_saas_scrape, url)
    return {"message": f"SaaS scraping for URL '{url}' initiated in the background."}

@router.get("/", response_model=List[SaaSInfo])
async def read_all_saas_info_endpoint(
    skip: int = 0, 
    limit: int = 100, 
    query_bus = Depends(get_query_bus)
):
    saas_info_list = await query_bus.dispatch(ListSaaSInfoQuery(skip=skip, limit=limit))
    return saas_info_list

@router.get("/{saas_info_id}", response_model=SaaSInfo)
async def read_saas_info_endpoint(
    saas_info_id: int, 
    query_bus = Depends(get_query_bus)
):
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    return saas_info

@router.put("/{saas_info_id}", response_model=SaaSInfo)
async def update_saas_info_endpoint(
    saas_info_id: int, 
    saas_info_update: SaaSInfoCreate, # Using Create schema for update for simplicity, adjust if needed
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    existing_saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if not existing_saas_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")

    command = UpdateSaaSInfoCommand(
        saas_info_id=saas_info_id,
        name=saas_info_update.name,
        one_liner=saas_info_update.one_liner,
        target_segments=saas_info_update.target_segments
    )
    updated_saas_info = await command_bus.dispatch(command)
    if updated_saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found after update attempt")
    return SaaSInfo.model_validate(updated_saas_info)

@router.delete("/{saas_info_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saas_info_endpoint( # type: ignore
    saas_info_id: int, 
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    existing_saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if not existing_saas_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    
    command = DeleteSaaSInfoCommand(saas_info_id=saas_info_id)
    deleted = await command_bus.dispatch(command)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete SaaS Info")
    return {"message": "SaaS Info deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import List

from app.schemas import schemas
from app.core.dependencies import get_command_bus, get_query_bus
from app.core.cqrs import CommandBus, QueryBus
from app.commands.lead_commands import CreateLeadCommand, UpdateLeadCommand, DeleteLeadCommand
from app.queries.lead_queries import GetLeadByIdQuery, ListLeadsQuery
from app.queries.saas_info_queries import GetSaaSInfoByIdQuery
from app.services.leads_service import perform_leads_search # Keep for now, will refactor later

router = APIRouter(
    prefix="/saas-info/{saas_info_id}/leads",
    tags=["Leads"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Lead, status_code=status.HTTP_201_CREATED)
async def create_lead_endpoint(
    saas_info_id: int, 
    lead_create: schemas.LeadCreate, 
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    
    command = CreateLeadCommand(
        competitor_name=lead_create.competitor_name,
        strengths=lead_create.strengths,
        weaknesses=lead_create.weaknesses,
        related_subreddits=lead_create.related_subreddits,
        saas_info_id=saas_info_id
    )
    created_lead = await command_bus.dispatch(command)
    return schemas.Lead.model_validate(created_lead)

@router.get("/", response_model=List[schemas.Lead])
async def read_leads_for_saas_info_endpoint(
    saas_info_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    query_bus = Depends(get_query_bus)
):
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    
    leads = await query_bus.dispatch(ListLeadsQuery(saas_info_id=saas_info_id, skip=skip, limit=limit))
    return leads

@router.get("/{lead_id}", response_model=schemas.Lead)
async def read_lead_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    query_bus = Depends(get_query_bus)
):
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    
    lead = await query_bus.dispatch(GetLeadByIdQuery(lead_id=lead_id))
    if lead is None or lead.saas_info_id != saas_info_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found for this SaaS Info")
    return lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    
    lead = await query_bus.dispatch(GetLeadByIdQuery(lead_id=lead_id))
    if lead is None or lead.saas_info_id != saas_info_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found for this SaaS Info")
    
    command = DeleteLeadCommand(lead_id=lead_id)
    deleted = await command_bus.dispatch(command)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete Lead")
    return {"message": "Lead deleted successfully"}

@router.post("/search", status_code=status.HTTP_202_ACCEPTED)
async def trigger_leads_search_endpoint(
    saas_info_id: int, 
    background_tasks: BackgroundTasks, 
    query_bus = Depends(get_query_bus)
):
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    
    background_tasks.add_task(perform_leads_search, saas_info_id)
    return {"message": "Lead search initiated in the background."}

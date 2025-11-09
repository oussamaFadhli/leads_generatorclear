from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.schemas import schemas
from app.crud import crud
from app.core.database import get_db
from app.services.leads_service import perform_leads_search

router = APIRouter(
    prefix="/saas-info/{saas_info_id}/leads",
    tags=["Leads"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Lead)
def create_lead_endpoint(
    saas_info_id: int, 
    lead: schemas.LeadCreate, 
    db: Session = Depends(get_db)
):
    db_saas_info = crud.get_saas_info(db, saas_info_id=saas_info_id)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    return crud.create_lead(db=db, lead=lead, saas_info_id=saas_info_id)

@router.get("/", response_model=List[schemas.Lead])
def read_leads_for_saas_info_endpoint(
    saas_info_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    db_saas_info = crud.get_saas_info(db, saas_info_id=saas_info_id)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    leads = crud.get_leads_for_saas_info(db, saas_info_id=saas_info_id, skip=skip, limit=limit)
    return leads

@router.get("/{lead_id}", response_model=schemas.Lead)
def read_lead_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    db: Session = Depends(get_db)
):
    db_saas_info = crud.get_saas_info(db, saas_info_id=saas_info_id)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    db_lead = crud.get_lead(db, lead_id=lead_id)
    if db_lead is None or db_lead.saas_info_id != saas_info_id:
        raise HTTPException(status_code=404, detail="Lead not found for this SaaS Info")
    return db_lead

@router.delete("/{lead_id}", response_model=schemas.Lead)
def delete_lead_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    db: Session = Depends(get_db)
):
    db_saas_info = crud.get_saas_info(db, saas_info_id=saas_info_id)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    db_lead = crud.get_lead(db, lead_id=lead_id)
    if db_lead is None or db_lead.saas_info_id != saas_info_id:
        raise HTTPException(status_code=404, detail="Lead not found for this SaaS Info")
    return crud.delete_lead(db=db, lead_id=lead_id)

@router.post("/search", status_code=202)
async def trigger_leads_search_endpoint(
    saas_info_id: int, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    db_saas_info = crud.get_saas_info(db, saas_info_id=saas_info_id)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    
    background_tasks.add_task(perform_leads_search, saas_info_id, db)
    return {"message": "Lead search initiated in the background."}

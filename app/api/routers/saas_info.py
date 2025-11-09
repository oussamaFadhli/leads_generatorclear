from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.schemas import schemas
from app.crud import crud
from app.core.database import get_db
from app.services.saas_scraper_service import perform_saas_scrape

router = APIRouter(
    prefix="/saas-info",
    tags=["SaaS Info"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.SaaSInfo)
def create_saas_info_endpoint(saas_info: schemas.SaaSInfoCreate, db: Session = Depends(get_db)):
    db_saas_info = crud.get_saas_info_by_name(db, name=saas_info.name)
    if db_saas_info:
        raise HTTPException(status_code=400, detail="SaaS Info with this name already exists")
    return crud.create_saas_info(db=db, saas_info=saas_info)

@router.post("/scrape", status_code=202)
async def trigger_saas_scrape_endpoint(
    url: str, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    background_tasks.add_task(perform_saas_scrape, url, db)
    return {"message": f"SaaS scraping for URL '{url}' initiated in the background."}

@router.get("/", response_model=List[schemas.SaaSInfo])
def read_all_saas_info_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    saas_info = crud.get_all_saas_info(db, skip=skip, limit=limit)
    return saas_info

@router.get("/{saas_info_id}", response_model=schemas.SaaSInfo)
def read_saas_info_endpoint(saas_info_id: int, db: Session = Depends(get_db)):
    db_saas_info = crud.get_saas_info(db, saas_info_id=saas_info_id)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    return db_saas_info

@router.put("/{saas_info_id}", response_model=schemas.SaaSInfo)
def update_saas_info_endpoint(saas_info_id: int, saas_info: schemas.SaaSInfoCreate, db: Session = Depends(get_db)):
    db_saas_info = crud.update_saas_info(db, saas_info_id=saas_info_id, saas_info=saas_info)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    return db_saas_info

@router.delete("/{saas_info_id}", response_model=schemas.SaaSInfo)
def delete_saas_info_endpoint(saas_info_id: int, db: Session = Depends(get_db)):
    db_saas_info = crud.delete_saas_info(db, saas_info_id=saas_info_id)
    if db_saas_info is None:
        raise HTTPException(status_code=404, detail="SaaS Info not found")
    return db_saas_info

from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Query
from app.schemas.schemas import SaaSInfo as SaaSInfoSchema # Assuming this is your Pydantic schema for SaaSInfo

class GetSaaSInfoByIdQuery(BaseModel, Query[SaaSInfoSchema]):
    saas_info_id: int

class GetSaaSInfoByNameQuery(BaseModel, Query[SaaSInfoSchema]):
    name: str

class ListSaaSInfoQuery(BaseModel, Query[List[SaaSInfoSchema]]):
    skip: int = 0
    limit: int = 100

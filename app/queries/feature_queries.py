from pydantic import BaseModel
from typing import List, Optional
from app.core.cqrs import Query
from app.schemas.schemas import Feature as FeatureSchema

class GetFeatureByIdQuery(BaseModel, Query[FeatureSchema]):
    feature_id: int

class GetFeatureByNameQuery(BaseModel, Query[FeatureSchema]):
    name: str

class ListFeaturesQuery(BaseModel, Query[List[FeatureSchema]]):
    skip: int = 0
    limit: int = 100
    saas_info_id: Optional[int] = None

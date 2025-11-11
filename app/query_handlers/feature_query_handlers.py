from typing import List, Optional
from app.core.cqrs import QueryHandler
from app.queries.feature_queries import GetFeatureByIdQuery, GetFeatureByNameQuery, ListFeaturesQuery
from app.repositories import FeatureRepository
from app.schemas.schemas import Feature as FeatureSchema
from sqlalchemy.future import select

class GetFeatureByIdQueryHandler(QueryHandler[GetFeatureByIdQuery, Optional[FeatureSchema]]):
    def __init__(self, feature_repo: FeatureRepository):
        self.feature_repo = feature_repo

    async def handle(self, query: GetFeatureByIdQuery) -> Optional[FeatureSchema]:
        feature = await self.feature_repo.get(query.feature_id)
        return FeatureSchema.model_validate(feature) if feature else None

class GetFeatureByNameQueryHandler(QueryHandler[GetFeatureByNameQuery, Optional[FeatureSchema]]):
    def __init__(self, feature_repo: FeatureRepository):
        self.feature_repo = feature_repo

    async def handle(self, query: GetFeatureByNameQuery) -> Optional[FeatureSchema]:
        feature = await self.feature_repo.get_by_name(query.name)
        return FeatureSchema.model_validate(feature) if feature else None

class ListFeaturesQueryHandler(QueryHandler[ListFeaturesQuery, List[FeatureSchema]]):
    def __init__(self, feature_repo: FeatureRepository):
        self.feature_repo = feature_repo

    async def handle(self, query: ListFeaturesQuery) -> List[FeatureSchema]:
        stmt = select(self.feature_repo.model)
        if query.saas_info_id:
            stmt = stmt.filter(self.feature_repo.model.saas_info_id == query.saas_info_id)
        
        result = await self.feature_repo.db.execute(stmt.offset(query.skip).limit(query.limit))
        features_list = result.scalars().all()
        return [FeatureSchema.model_validate(feature) for feature in features_list]

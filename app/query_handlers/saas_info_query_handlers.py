from typing import List, Optional
from app.core.cqrs import QueryHandler
from app.queries.saas_info_queries import GetSaaSInfoByIdQuery, GetSaaSInfoByNameQuery, ListSaaSInfoQuery
from app.repositories import SaaSInfoRepository
from app.schemas.schemas import SaaSInfo as SaaSInfoSchema

class GetSaaSInfoByIdQueryHandler(QueryHandler[GetSaaSInfoByIdQuery, Optional[SaaSInfoSchema]]):
    def __init__(self, saas_info_repo: SaaSInfoRepository):
        self.saas_info_repo = saas_info_repo

    async def handle(self, query: GetSaaSInfoByIdQuery) -> Optional[SaaSInfoSchema]:
        saas_info = await self.saas_info_repo.get(query.saas_info_id)
        return SaaSInfoSchema.model_validate(saas_info) if saas_info else None

class GetSaaSInfoByNameQueryHandler(QueryHandler[GetSaaSInfoByNameQuery, Optional[SaaSInfoSchema]]):
    def __init__(self, saas_info_repo: SaaSInfoRepository):
        self.saas_info_repo = saas_info_repo

    async def handle(self, query: GetSaaSInfoByNameQuery) -> Optional[SaaSInfoSchema]:
        saas_info = await self.saas_info_repo.get_by_name(query.name)
        return SaaSInfoSchema.model_validate(saas_info) if saas_info else None

class ListSaaSInfoQueryHandler(QueryHandler[ListSaaSInfoQuery, List[SaaSInfoSchema]]):
    def __init__(self, saas_info_repo: SaaSInfoRepository):
        self.saas_info_repo = saas_info_repo

    async def handle(self, query: ListSaaSInfoQuery) -> List[SaaSInfoSchema]:
        saas_info_list = await self.saas_info_repo.get_multi(skip=query.skip, limit=query.limit)
        return [SaaSInfoSchema.model_validate(saas_info) for saas_info in saas_info_list]

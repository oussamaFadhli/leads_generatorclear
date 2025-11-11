from typing import List, Optional
from app.core.cqrs import QueryHandler
from app.queries.lead_queries import (
    GetLeadByIdQuery,
    GetLeadByCompetitorNameQuery,
    ListLeadsQuery,
    CheckIfAlreadyPostedToSubredditQuery,
)
from app.repositories import LeadRepository, RedditPostRepository
from app.schemas.schemas import Lead as LeadSchema

class GetLeadByIdQueryHandler(QueryHandler[GetLeadByIdQuery, Optional[LeadSchema]]):
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def handle(self, query: GetLeadByIdQuery) -> Optional[LeadSchema]:
        lead = await self.lead_repo.get(query.lead_id)
        return LeadSchema.model_validate(lead) if lead else None

class GetLeadByCompetitorNameQueryHandler(QueryHandler[GetLeadByCompetitorNameQuery, Optional[LeadSchema]]):
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def handle(self, query: GetLeadByCompetitorNameQuery) -> Optional[LeadSchema]:
        lead = await self.lead_repo.get_by_competitor_name(query.competitor_name)
        return LeadSchema.model_validate(lead) if lead else None

class ListLeadsQueryHandler(QueryHandler[ListLeadsQuery, List[LeadSchema]]):
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo

    async def handle(self, query: ListLeadsQuery) -> List[LeadSchema]:
        leads_list = await self.lead_repo.get_multi(skip=query.skip, limit=query.limit)
        return [LeadSchema.model_validate(lead) for lead in leads_list]

class CheckIfAlreadyPostedToSubredditQueryHandler(QueryHandler[CheckIfAlreadyPostedToSubredditQuery, bool]):
    def __init__(self, reddit_post_repo: RedditPostRepository):
        self.reddit_post_repo = reddit_post_repo

    async def handle(self, query: CheckIfAlreadyPostedToSubredditQuery) -> bool:
        return await self.reddit_post_repo.has_posted_to_subreddit(
            lead_id=query.lead_id,
            generated_title=query.generated_title,
            subreddit_name=query.subreddit_name,
        )

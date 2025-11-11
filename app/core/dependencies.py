from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.cqrs import CommandBus, QueryBus
from app.repositories import (
    SaaSInfoRepository, LeadRepository, RedditPostRepository,
    RedditCommentRepository, FeatureRepository, PricingPlanRepository
)
from app.command_handlers import (
    CreateSaaSInfoCommandHandler, UpdateSaaSInfoCommandHandler, DeleteSaaSInfoCommandHandler,
    CreateLeadCommandHandler, UpdateLeadCommandHandler, DeleteLeadCommandHandler,
    CreateRedditPostCommandHandler, UpdateRedditPostCommandHandler, DeleteRedditPostCommandHandler,
    CreateRedditCommentCommandHandler, UpdateRedditCommentCommandHandler, DeleteRedditCommentCommandHandler,
    CreateFeatureCommandHandler, UpdateFeatureCommandHandler, DeleteFeatureCommandHandler,
    CreatePricingPlanCommandHandler, UpdatePricingPlanCommandHandler, DeletePricingPlanCommandHandler
)
from app.query_handlers import (
    GetSaaSInfoByIdQueryHandler, GetSaaSInfoByNameQueryHandler, ListSaaSInfoQueryHandler,
    GetLeadByIdQueryHandler, GetLeadByCompetitorNameQueryHandler, ListLeadsQueryHandler,
    CheckIfAlreadyPostedToSubredditQueryHandler,
    GetRedditPostByIdQueryHandler, GetRedditPostByTitleQueryHandler, ListRedditPostsQueryHandler,
    GetRedditCommentByIdQueryHandler, GetRedditCommentByCommentIdQueryHandler, ListRedditCommentsQueryHandler,
    GetFeatureByIdQueryHandler, GetFeatureByNameQueryHandler, ListFeaturesQueryHandler,
    GetPricingPlanByIdQueryHandler, GetPricingPlanByPlanNameQueryHandler, ListPricingPlansQueryHandler
)
from app.commands import (
    CreateSaaSInfoCommand, UpdateSaaSInfoCommand, DeleteSaaSInfoCommand,
    CreateLeadCommand, UpdateLeadCommand, DeleteLeadCommand,
    CreateRedditPostCommand, UpdateRedditPostCommand, DeleteRedditPostCommand,
    CreateRedditCommentCommand, UpdateRedditCommentCommand, DeleteRedditCommentCommand,
    CreateFeatureCommand, UpdateFeatureCommand, DeleteFeatureCommand,
    CreatePricingPlanCommand, UpdatePricingPlanCommand, DeletePricingPlanCommand
)
from app.queries import (
    GetSaaSInfoByIdQuery, GetSaaSInfoByNameQuery, ListSaaSInfoQuery,
    GetLeadByIdQuery, GetLeadByCompetitorNameQuery, ListLeadsQuery, CheckIfAlreadyPostedToSubredditQuery,
    GetRedditPostByIdQuery, GetRedditPostByTitleQuery, ListRedditPostsQuery,
    GetRedditCommentByIdQuery, GetRedditCommentByCommentIdQuery, ListRedditCommentsQuery,
    GetFeatureByIdQuery, GetFeatureByNameQuery, ListFeaturesQuery,
    GetPricingPlanByIdQuery, GetPricingPlanByPlanNameQuery, ListPricingPlansQuery
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

def create_command_bus(db: AsyncSession) -> CommandBus:
    command_bus = CommandBus()
    
    # Register SaaSInfo Command Handlers
    command_bus.register_handler(CreateSaaSInfoCommand, CreateSaaSInfoCommandHandler(SaaSInfoRepository(db)))
    command_bus.register_handler(UpdateSaaSInfoCommand, UpdateSaaSInfoCommandHandler(SaaSInfoRepository(db)))
    command_bus.register_handler(DeleteSaaSInfoCommand, DeleteSaaSInfoCommandHandler(SaaSInfoRepository(db)))

    # Register Lead Command Handlers
    command_bus.register_handler(CreateLeadCommand, CreateLeadCommandHandler(LeadRepository(db)))
    command_bus.register_handler(UpdateLeadCommand, UpdateLeadCommandHandler(LeadRepository(db)))
    command_bus.register_handler(DeleteLeadCommand, DeleteLeadCommandHandler(LeadRepository(db)))

    # Register RedditPost Command Handlers
    command_bus.register_handler(CreateRedditPostCommand, CreateRedditPostCommandHandler(RedditPostRepository(db)))
    command_bus.register_handler(UpdateRedditPostCommand, UpdateRedditPostCommandHandler(RedditPostRepository(db)))
    command_bus.register_handler(DeleteRedditPostCommand, DeleteRedditPostCommandHandler(RedditPostRepository(db)))

    # Register RedditComment Command Handlers
    command_bus.register_handler(CreateRedditCommentCommand, CreateRedditCommentCommandHandler(RedditCommentRepository(db)))
    command_bus.register_handler(UpdateRedditCommentCommand, UpdateRedditCommentCommandHandler(RedditCommentRepository(db)))
    command_bus.register_handler(DeleteRedditCommentCommand, DeleteRedditCommentCommandHandler(RedditCommentRepository(db)))

    # Register Feature Command Handlers
    command_bus.register_handler(CreateFeatureCommand, CreateFeatureCommandHandler(FeatureRepository(db)))
    command_bus.register_handler(UpdateFeatureCommand, UpdateFeatureCommandHandler(FeatureRepository(db)))
    command_bus.register_handler(DeleteFeatureCommand, DeleteFeatureCommandHandler(FeatureRepository(db)))

    # Register PricingPlan Command Handlers
    command_bus.register_handler(CreatePricingPlanCommand, CreatePricingPlanCommandHandler(PricingPlanRepository(db)))
    command_bus.register_handler(UpdatePricingPlanCommand, UpdatePricingPlanCommandHandler(PricingPlanRepository(db)))
    command_bus.register_handler(DeletePricingPlanCommand, DeletePricingPlanCommandHandler(PricingPlanRepository(db)))

    return command_bus

async def get_command_bus(db: AsyncSession = Depends(get_db)) -> CommandBus:
    return create_command_bus(db)

def create_query_bus(db: AsyncSession) -> QueryBus:
    query_bus = QueryBus()

    # Register SaaSInfo Query Handlers
    query_bus.register_handler(GetSaaSInfoByIdQuery, GetSaaSInfoByIdQueryHandler(SaaSInfoRepository(db)))
    query_bus.register_handler(GetSaaSInfoByNameQuery, GetSaaSInfoByNameQueryHandler(SaaSInfoRepository(db)))
    query_bus.register_handler(ListSaaSInfoQuery, ListSaaSInfoQueryHandler(SaaSInfoRepository(db)))

    # Register Lead Query Handlers
    query_bus.register_handler(GetLeadByIdQuery, GetLeadByIdQueryHandler(LeadRepository(db)))
    query_bus.register_handler(GetLeadByCompetitorNameQuery, GetLeadByCompetitorNameQueryHandler(LeadRepository(db)))
    query_bus.register_handler(ListLeadsQuery, ListLeadsQueryHandler(LeadRepository(db)))
    query_bus.register_handler(
        CheckIfAlreadyPostedToSubredditQuery,
        CheckIfAlreadyPostedToSubredditQueryHandler(RedditPostRepository(db))
    )

    # Register RedditPost Query Handlers
    query_bus.register_handler(GetRedditPostByIdQuery, GetRedditPostByIdQueryHandler(RedditPostRepository(db)))
    query_bus.register_handler(GetRedditPostByTitleQuery, GetRedditPostByTitleQueryHandler(RedditPostRepository(db)))
    query_bus.register_handler(ListRedditPostsQuery, ListRedditPostsQueryHandler(RedditPostRepository(db)))

    # Register RedditComment Query Handlers
    query_bus.register_handler(GetRedditCommentByIdQuery, GetRedditCommentByIdQueryHandler(RedditCommentRepository(db)))
    query_bus.register_handler(GetRedditCommentByCommentIdQuery, GetRedditCommentByCommentIdQueryHandler(RedditCommentRepository(db)))
    query_bus.register_handler(ListRedditCommentsQuery, ListRedditCommentsQueryHandler(RedditCommentRepository(db)))

    # Register Feature Query Handlers
    query_bus.register_handler(GetFeatureByIdQuery, GetFeatureByIdQueryHandler(FeatureRepository(db)))
    query_bus.register_handler(GetFeatureByNameQuery, GetFeatureByNameQueryHandler(FeatureRepository(db)))
    query_bus.register_handler(ListFeaturesQuery, ListFeaturesQueryHandler(FeatureRepository(db)))

    # Register PricingPlan Query Handlers
    query_bus.register_handler(GetPricingPlanByIdQuery, GetPricingPlanByIdQueryHandler(PricingPlanRepository(db)))
    query_bus.register_handler(GetPricingPlanByPlanNameQuery, GetPricingPlanByPlanNameQueryHandler(PricingPlanRepository(db)))
    query_bus.register_handler(ListPricingPlansQuery, ListPricingPlansQueryHandler(PricingPlanRepository(db)))

    return query_bus

async def get_query_bus(db: AsyncSession = Depends(get_db)) -> QueryBus:
    return create_query_bus(db)

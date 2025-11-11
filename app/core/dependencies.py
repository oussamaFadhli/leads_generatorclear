from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import praw # Import praw
from app.core.config import settings # Import settings
from app.core.database import AsyncSessionLocal
from app.core.cqrs import CommandBus, QueryBus
from app.repositories import (
    SaaSInfoRepository, LeadRepository, RedditPostRepository,
    RedditCommentRepository, FeatureRepository, PricingPlanRepository, TaskRepository
)
from app.services.task_service import TaskService
from app.core.websocket_manager import websocket_manager # Import websocket_manager
from app.command_handlers import (
    CreateSaaSInfoCommandHandler, UpdateSaaSInfoCommandHandler, DeleteSaaSInfoCommandHandler,
    CreateLeadCommandHandler, UpdateLeadCommandHandler, DeleteLeadCommandHandler,
    CreateRedditPostCommandHandler, UpdateRedditPostCommandHandler, DeleteRedditPostCommandHandler,
    CreateRedditCommentCommandHandler, UpdateRedditCommentCommandHandler, DeleteRedditCommentCommandHandler,
    CreateFeatureCommandHandler, UpdateFeatureCommandHandler, DeleteFeatureCommandHandler,
    CreatePricingPlanCommandHandler, UpdatePricingPlanCommandHandler, DeletePricingPlanCommandHandler,
    CreateTaskCommandHandler, UpdateTaskStatusCommandHandler
)
from app.query_handlers import (
    GetSaaSInfoByIdQueryHandler, GetSaaSInfoByNameQueryHandler, ListSaaSInfoQueryHandler,
    GetLeadByIdQueryHandler, GetLeadByCompetitorNameQueryHandler, ListLeadsQueryHandler,
    CheckIfAlreadyPostedToSubredditQueryHandler,
    GetRedditPostByIdQueryHandler, GetRedditPostByTitleQueryHandler, ListRedditPostsQueryHandler,
    GetRedditCommentByIdQueryHandler, GetRedditCommentByCommentIdQueryHandler, ListRedditCommentsQueryHandler,
    GetFeatureByIdQueryHandler, GetFeatureByNameQueryHandler, ListFeaturesQueryHandler,
    GetPricingPlanByIdQueryHandler, GetPricingPlanByPlanNameQueryHandler, ListPricingPlansQueryHandler,
    GetTaskQueryHandler, GetAllTasksQueryHandler, GetTasksByAgentIdQueryHandler
)
from app.commands import (
    CreateSaaSInfoCommand, UpdateSaaSInfoCommand, DeleteSaaSInfoCommand,
    CreateLeadCommand, UpdateLeadCommand, DeleteLeadCommand,
    CreateRedditPostCommand, UpdateRedditPostCommand, DeleteRedditPostCommand,
    CreateRedditCommentCommand, UpdateRedditCommentCommand, DeleteRedditCommentCommand,
    CreateFeatureCommand, UpdateFeatureCommand, DeleteFeatureCommand,
    CreatePricingPlanCommand, UpdatePricingPlanCommand, DeletePricingPlanCommand,
    CreateTaskCommand, UpdateTaskStatusCommand
)
from app.queries import (
    GetSaaSInfoByIdQuery, GetSaaSInfoByNameQuery, ListSaaSInfoQuery,
    GetLeadByIdQuery, GetLeadByCompetitorNameQuery, ListLeadsQuery, CheckIfAlreadyPostedToSubredditQuery,
    GetRedditPostByIdQuery, GetRedditPostByTitleQuery, ListRedditPostsQuery,
    GetRedditCommentByIdQuery, GetRedditCommentByCommentIdQuery, ListRedditCommentsQuery,
    GetFeatureByIdQuery, GetFeatureByNameQuery, ListFeaturesQuery,
    GetPricingPlanByIdQuery, GetPricingPlanByPlanNameQuery, ListPricingPlansQuery,
    GetTaskQuery, GetAllTasksQuery, GetTasksByAgentIdQuery
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

    # Register Task Command Handlers
    task_service = TaskService(TaskRepository(db), websocket_manager)
    command_bus.register_handler(CreateTaskCommand, CreateTaskCommandHandler(task_service))
    command_bus.register_handler(UpdateTaskStatusCommand, UpdateTaskStatusCommandHandler(task_service))

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

    # Register Task Query Handlers
    task_service = TaskService(TaskRepository(db), websocket_manager)
    query_bus.register_handler(GetTaskQuery, GetTaskQueryHandler(task_service))
    query_bus.register_handler(GetAllTasksQuery, GetAllTasksQueryHandler(task_service))
    query_bus.register_handler(GetTasksByAgentIdQuery, GetTasksByAgentIdQueryHandler(task_service))

    return query_bus

async def get_query_bus(db: AsyncSession = Depends(get_db)) -> QueryBus:
    return create_query_bus(db)

def get_reddit_instance() -> praw.Reddit:
    """Returns a configured PRAW Reddit instance."""
    return praw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent=settings.REDDIT_USER_AGENT,
        username=settings.REDDIT_USERNAME,
        password=settings.REDDIT_PASSWORD
    )

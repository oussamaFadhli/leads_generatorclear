import logging
from contextlib import asynccontextmanager
from typing import List, Optional, TYPE_CHECKING
from app.core.config import settings
from app.schemas import schemas
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession
from app.core.cqrs import CommandBus, QueryBus
from app.core.dependencies import create_command_bus, create_query_bus # Removed AsyncSessionLocal
from app.commands.lead_commands import CreateLeadCommand
from app.commands.reddit_post_commands import CreateRedditPostCommand
from app.commands.reddit_comment_commands import CreateRedditCommentCommand, UpdateRedditCommentCommand
from app.queries.saas_info_queries import GetSaaSInfoByIdQuery
from app.queries.lead_queries import GetLeadByIdQuery, ListLeadsQuery
from app.queries.reddit_post_queries import GetRedditPostByIdQuery, GetRedditPostByTitleQuery, ListRedditPostsQuery
from app.queries.reddit_comment_queries import GetRedditCommentByCommentIdQuery, GetRedditCommentByIdQuery, ListRedditCommentsQuery
from app.services.reddit import auth_service, account_service, scraping_service, generation_service, posting_service, preview_service
from app.core.websocket_manager import websocket_manager # Import WebSocket Manager
import json # Import json for WebSocket messages

if TYPE_CHECKING:
    from app.services.reddit import generation_service as GenerationServiceModule

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def perform_reddit_analysis(
    saas_info_id: int,
    lead_id: int,
    subreddit_name: str,
    db: AsyncSession, # Inject AsyncSession
):
    cmd_bus = create_command_bus(db)
    qry_bus = create_query_bus(db)

async def perform_reddit_analysis(
    saas_info_id: int,
    lead_id: int,
    subreddit_name: str,
    db: AsyncSession, # Inject AsyncSession
):
    cmd_bus = create_command_bus(db)
    qry_bus = create_query_bus(db)

    logging.info(f"Starting Reddit analysis for subreddit: {subreddit_name}, Lead ID: {lead_id}")

    reddit = auth_service.get_reddit_instance()
    if not reddit:
        return
    
    if not account_service.check_account_health(reddit):
        logging.error("Account health check failed. Aborting.")
        return

    saas_info_db = await qry_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if not saas_info_db:
        logging.error(f"SaaS Info with ID {saas_info_id} not found.")
        return

    fetched_posts = await scraping_service.fetch_reddit_posts(reddit, subreddit_name)
    if not fetched_posts:
        logging.warning(f"No posts fetched from r/{subreddit_name}. Aborting.")
        return

    for post_data in fetched_posts:
        # Check if post already exists to avoid duplicates
        existing_post = await qry_bus.dispatch(GetRedditPostByTitleQuery(title=post_data.title))
        if not existing_post:
            create_post_command = CreateRedditPostCommand(
                title=post_data.title,
                content=post_data.content,
                score=post_data.score,
                num_comments=post_data.num_comments,
                author=post_data.author,
                url=post_data.url,
                subreddits=post_data.subreddits if post_data.subreddits else [],
                lead_id=lead_id
            )
            await cmd_bus.dispatch(create_post_command)
            logging.info(f"Saved new Reddit post: {post_data.title}")
        else:
            logging.info(f"Reddit post '{post_data.title}' already exists. Skipping.")
    
    logging.info(f"Reddit analysis for r/{subreddit_name} completed.")

async def generate_reddit_posts(
    saas_info_id: int,
    post_id: int,
    db: AsyncSession, # Inject AsyncSession
) -> None:
    cmd_bus = create_command_bus(db)
    qry_bus = create_query_bus(db)

    try:
        await generation_service.generate_reddit_posts(saas_info_id, post_id, cmd_bus, qry_bus)
        logging.info(f"Generated Reddit posts for post {post_id}.")
    except Exception as e:
        logging.error(f"Error generating Reddit posts for post {post_id}: {e}", exc_info=True)

async def post_generated_reddit_post(
    post_id: int,
    db: AsyncSession, # Inject AsyncSession
) -> None:
    cmd_bus = create_command_bus(db)
    qry_bus = create_query_bus(db)

    try:
        await posting_service.post_generated_reddit_post(post_id, cmd_bus, qry_bus)
        logging.info(f"Posted generated Reddit post {post_id}.")
    except Exception as e:
        logging.error(f"Error posting generated Reddit post {post_id}: {e}", exc_info=True)

async def preview_generated_post(post_id: int, query_bus: QueryBus) -> Optional[dict]:
    return await preview_service.preview_generated_post(post_id, query_bus)

async def reply_to_reddit_post_comments(
    saas_info_id: int,
    reddit_post_url: str,
    db: AsyncSession, # Inject AsyncSession
):
    cmd_bus = create_command_bus(db)
    qry_bus = create_query_bus(db)

    logging.info(f"Starting process to reply to comments for Reddit post URL: {reddit_post_url}")

    reddit = auth_service.get_reddit_instance()
    if not reddit:
        return

    if not account_service.check_account_health(reddit):
        logging.error("Account health check failed. Aborting comment reply process.")
        return

    saas_info_db = await qry_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if not saas_info_db:
        logging.error(f"SaaS Info with ID {saas_info_id} not found.")
        return

    # First, try to find if this Reddit post already exists in our DB
    db_reddit_post = await qry_bus.dispatch(ListRedditPostsQuery(url=reddit_post_url, limit=1))
    db_reddit_post = db_reddit_post[0] if db_reddit_post else None

    if not db_reddit_post:
        # If not, we need to create a placeholder RedditPost entry to link comments to
        logging.info(f"Reddit post {reddit_post_url} not found in DB. Creating a placeholder entry.")
        post_title = f"Reddit Post: {reddit_post_url}"
        post_author = "unknown"
        submission = reddit.submission(url=reddit_post_url)
        post_title = submission.title
        post_author = str(submission.author)

        db_lead = await qry_bus.dispatch(ListLeadsQuery(saas_info_id=saas_info_id, limit=1))
        db_lead = db_lead[0] if db_lead else None

        if not db_lead:
            logging.warning(f"No lead found for SaaS Info ID {saas_info_id}. Creating a default lead.")
            create_lead_command = CreateLeadCommand(
                competitor_name=f"Default Lead for SaaS {saas_info_id}",
                strengths=["general problem solving"],
                weaknesses=["lack of specific focus"],
                related_subreddits=["general_discussion"],
                saas_info_id=saas_info_id
            )
            db_lead = await cmd_bus.dispatch(create_lead_command)
            logging.info(f"Created default Lead with ID: {db_lead.id} for SaaS Info ID: {saas_info_id}")

        create_reddit_post_command = CreateRedditPostCommand(
            title=post_title,
            content="Scraped post content placeholder.",
            score=0,
            num_comments=0,
            author=post_author,
            url=reddit_post_url,
            subreddits=[],
            lead_id=db_lead.id
        )
        db_reddit_post = await cmd_bus.dispatch(create_reddit_post_command)
        logging.info(f"Created placeholder RedditPost with ID: {db_reddit_post.id}")

    fetched_comments = await scraping_service.fetch_comments_from_post_url(reddit, reddit_post_url)
    if not fetched_comments:
        logging.warning(f"No comments fetched from {reddit_post_url}. Aborting comment reply process.")
        return

    for comment_data in fetched_comments:
        existing_comment = await qry_bus.dispatch(GetRedditCommentByCommentIdQuery(comment_id=comment_data.comment_id))
        if not existing_comment:
            create_comment_command = CreateRedditCommentCommand(
                comment_id=comment_data.comment_id,
                post_id=comment_data.post_id,
                author=comment_data.author,
                content=comment_data.content,
                score=comment_data.score,
                permalink=comment_data.permalink,
                reddit_post_db_id=db_reddit_post.id
            )
            await cmd_bus.dispatch(create_comment_command)
            logging.info(f"Saved new Reddit comment: {comment_data.comment_id}")
        else:
            logging.info(f"Reddit comment '{comment_data.comment_id}' already exists. Skipping.")

    # Retrieve comments from DB to ensure we have their internal IDs
    comments_from_db = await qry_bus.dispatch(ListRedditCommentsQuery(reddit_post_db_id=db_reddit_post.id))

    for comment_db in comments_from_db:
        if comment_db.is_replied:
            logging.info(f"Comment DB ID {comment_db.id} already replied to. Skipping.")
            continue

        generated_reply_content = await generation_service.generate_reddit_comment_reply(
            saas_info_id, 
            comment_db.content, 
            cmd_bus,
            qry_bus
        )

        if generated_reply_content:
            success = await posting_service.post_reddit_comment_reply(
                reddit, 
                comment_db.comment_id, 
                generated_reply_content, 
                cmd_bus, 
                qry_bus,
                comment_db.id
            )
            if success:
                logging.info(f"Successfully processed and replied to comment DB ID: {comment_db.id}")
            else:
                logging.error(f"Failed to post reply for comment DB ID: {comment_db.id}")
        else:
            logging.error(f"Failed to generate reply for comment DB ID: {comment_db.id}")
    
    logging.info(f"Completed processing replies for Reddit post URL: {reddit_post_url}")

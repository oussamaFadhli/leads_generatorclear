from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import List, Tuple
import praw # Import praw for Reddit instance

from app.schemas import schemas
from app.core.dependencies import get_command_bus, get_query_bus, get_reddit_instance # Assuming get_reddit_instance exists or will be created
from app.core.cqrs import CommandBus, QueryBus
from app.commands.reddit_post_commands import CreateRedditPostCommand, UpdateRedditPostCommand, DeleteRedditPostCommand
from app.commands.reddit_comment_commands import CreateRedditCommentCommand, UpdateRedditCommentCommand, DeleteRedditCommentCommand
from app.queries.reddit_post_queries import GetRedditPostByIdQuery, ListRedditPostsQuery
from app.queries.reddit_comment_queries import GetRedditCommentByIdQuery, ListRedditCommentsQuery
from app.queries.saas_info_queries import GetSaaSInfoByIdQuery
from app.queries.lead_queries import GetLeadByIdQuery
from app.services.reddit_service import (
    perform_reddit_analysis, 
    generate_reddit_posts, 
    post_generated_reddit_post,
    reply_to_reddit_post_comments # Import the new service function
)
from app.services.scraping_orchestrator_service import ScrapingOrchestratorService # Import the new service

router = APIRouter(
    prefix="/saas-info/{saas_info_id}/leads/{lead_id}/reddit-posts",
    tags=["Reddit Posts"],
    responses={404: {"description": "Not found"}},
)

# New router for comment replies, not tied to a specific lead_id in the path
comments_router = APIRouter(
    prefix="/saas-info/{saas_info_id}/reddit-comments",
    tags=["Reddit Comments"],
    responses={404: {"description": "Not found"}},
)

async def verify_lead_and_saas_info(saas_info_id: int, lead_id: int, query_bus: QueryBus) -> Tuple[schemas.SaaSInfo, schemas.Lead]:
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    lead = await query_bus.dispatch(GetLeadByIdQuery(lead_id=lead_id))
    if lead is None or lead.saas_info_id != saas_info_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found for this SaaS Info")
    return saas_info, lead

@router.post("/", response_model=schemas.RedditPost, status_code=status.HTTP_201_CREATED)
async def create_reddit_post_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    post_create: schemas.RedditPostCreate, 
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    
    command = CreateRedditPostCommand(
        title=post_create.title,
        content=post_create.content,
        score=post_create.score,
        num_comments=post_create.num_comments,
        author=post_create.author,
        url=post_create.url,
        subreddits=post_create.subreddits if post_create.subreddits else [],
        lead_id=lead_id
    )
    created_post = await command_bus.dispatch(command)
    return schemas.RedditPost.model_validate(created_post)

@router.get("/", response_model=List[schemas.RedditPost])
async def read_reddit_posts_for_lead_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    posts = await query_bus.dispatch(ListRedditPostsQuery(lead_id=lead_id, skip=skip, limit=limit))
    return posts

@router.get("/{post_id}", response_model=schemas.RedditPost)
async def read_reddit_post_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    post_id: int, 
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    post = await query_bus.dispatch(GetRedditPostByIdQuery(reddit_post_id=post_id))
    if post is None or post.lead_id != lead_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reddit Post not found for this Lead")
    return post

@router.put("/{post_id}", response_model=schemas.RedditPost)
async def update_reddit_post_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    post_id: int, 
    post_update: schemas.RedditPostUpdate, 
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    existing_post = await query_bus.dispatch(GetRedditPostByIdQuery(reddit_post_id=post_id))
    if not existing_post or existing_post.lead_id != lead_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reddit Post not found for this Lead")
    
    command = UpdateRedditPostCommand(
        reddit_post_id=post_id,
        title=post_update.title,
        content=post_update.content,
        score=post_update.score,
        num_comments=post_update.num_comments,
        author=post_update.author,
        url=post_update.url,
        subreddits=post_update.subreddits,
        lead_score=post_update.lead_score,
        score_justification=post_update.score_justification,
        generated_title=post_update.generated_title,
        generated_content=post_update.generated_content,
        is_posted=post_update.is_posted,
        ai_generated=post_update.ai_generated,
        posted_url=post_update.posted_url
    )
    updated_post = await command_bus.dispatch(command)
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update Reddit Post")
    return schemas.RedditPost.model_validate(updated_post)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reddit_post_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    post_id: int, 
    command_bus = Depends(get_command_bus),
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    existing_post = await query_bus.dispatch(GetRedditPostByIdQuery(reddit_post_id=post_id))
    if not existing_post or existing_post.lead_id != lead_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reddit Post not found for this Lead")
    
    command = DeleteRedditPostCommand(reddit_post_id=post_id)
    deleted = await command_bus.dispatch(command)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete Reddit Post")
    return {"message": "Reddit Post deleted successfully"}

@comments_router.post("/reply-to-comments", status_code=status.HTTP_202_ACCEPTED)
async def trigger_reply_to_comments_endpoint(
    saas_info_id: int,
    reddit_post_url: str,
    background_tasks: BackgroundTasks,
    query_bus = Depends(get_query_bus)
):
    saas_info = await query_bus.dispatch(GetSaaSInfoByIdQuery(saas_info_id=saas_info_id))
    if saas_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SaaS Info not found")
    
    background_tasks.add_task(reply_to_reddit_post_comments, saas_info_id, reddit_post_url)
    return {"message": f"Initiated AI-powered replies to comments for Reddit post: {reddit_post_url}."}

@router.post("/analyze/{subreddit_name}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_reddit_analysis_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    subreddit_name: str,
    background_tasks: BackgroundTasks, 
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    
    background_tasks.add_task(perform_reddit_analysis, saas_info_id, lead_id, subreddit_name)
    return {"message": f"Reddit analysis for subreddit '{subreddit_name}' initiated in the background."}

@router.post("/generate/{post_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_post_generation_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    post_id: int,
    background_tasks: BackgroundTasks, 
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    post = await query_bus.dispatch(GetRedditPostByIdQuery(reddit_post_id=post_id))
    if post is None or post.lead_id != lead_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reddit Post not found for this Lead")
    
    background_tasks.add_task(generate_reddit_posts, saas_info_id, post_id)
    return {"message": f"Reddit post generation for post ID {post_id} initiated in the background."}

@router.post("/post/{post_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_reddit_post_endpoint(
    saas_info_id: int, 
    lead_id: int, 
    post_id: int,
    background_tasks: BackgroundTasks, 
    query_bus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    post = await query_bus.dispatch(GetRedditPostByIdQuery(reddit_post_id=post_id))
    if post is None or post.lead_id != lead_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reddit Post not found for this Lead")
    if not post.generated_title or not post.generated_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post content not generated yet.")
    
    background_tasks.add_task(post_generated_reddit_post, post_id)
    return {"message": f"Reddit post ID {post_id} scheduled for posting."}

@router.post("/scrape/{subreddit_name}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_reddit_scraping_endpoint(
    saas_info_id: int,
    lead_id: int,
    subreddit_name: str,
    client_id: str, # Client ID for WebSocket tracking
    background_tasks: BackgroundTasks,
    reddit_instance: praw.Reddit = Depends(get_reddit_instance), # Inject Reddit instance
    command_bus: CommandBus = Depends(get_command_bus),
    query_bus: QueryBus = Depends(get_query_bus)
):
    await verify_lead_and_saas_info(saas_info_id, lead_id, query_bus)
    
    orchestrator_service = ScrapingOrchestratorService(command_bus)
    
    background_tasks.add_task(
        orchestrator_service.orchestrate_reddit_scraping,
        reddit_instance,
        subreddit_name,
        10, # Default limit for now, can be made configurable
        client_id,
        f"lead_{lead_id}_saas_{saas_info_id}" # Agent ID for the task
    )
    return {"message": f"Reddit scraping for subreddit '{subreddit_name}' initiated in the background. Task updates will be sent to client '{client_id}'."}

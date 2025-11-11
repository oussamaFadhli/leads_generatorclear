import logging
from typing import List, Dict, Any
import praw
from app.core.cqrs import CommandBus
from app.commands.task_commands import CreateTaskCommand, UpdateTaskStatusCommand
from app.services.reddit.scraping_service import fetch_reddit_posts, fetch_comments_from_post_url
from app.schemas.schemas import RedditPostCreate, RedditCommentCreate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ScrapingOrchestratorService:
    def __init__(self, command_bus: CommandBus):
        self.command_bus = command_bus

    async def orchestrate_reddit_scraping(
        self,
        reddit_instance: praw.Reddit,
        subreddit_name: str,
        limit: int,
        client_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        task_name = f"Scraping Reddit for r/{subreddit_name}"
        task_id = None
        try:
            # 1. Create a new task
            create_task_command = CreateTaskCommand(
                agent_id=client_id, # Using client_id as agent_id for task tracking
                task_name=task_name,
                status="pending",
                result_data={"subreddit": subreddit_name, "limit": limit}
            )
            # The command handler will create the task and send initial WebSocket update
            created_task = await self.command_bus.dispatch(create_task_command)
            task_id = created_task.id # Assuming dispatch returns the created task with ID

            # 2. Update task status to running
            await self.command_bus.dispatch(
                UpdateTaskStatusCommand(
                    task_id=task_id,
                    status="running",
                    result_data={"message": "Scraping in progress..."}
                )
            )

            # 3. Fetch posts
            posts: List[RedditPostCreate] = await fetch_reddit_posts(reddit_instance, subreddit_name, limit)
            
            # 4. Fetch comments for each post (optional, depending on requirements)
            all_comments: List[RedditCommentCreate] = []
            for post in posts:
                comments = await fetch_comments_from_post_url(reddit_instance, post.url)
                all_comments.extend(comments)

            # 5. Update task status to completed
            result_data = {
                "subreddit": subreddit_name,
                "posts_fetched": len(posts),
                "comments_fetched": len(all_comments),
                "status": "completed",
                "data": {
                    "posts": [post.dict() for post in posts],
                    "comments": [comment.dict() for comment in all_comments]
                }
            }
            await self.command_bus.dispatch(
                UpdateTaskStatusCommand(
                    task_id=task_id,
                    status="completed",
                    result_data=result_data
                )
            )
            logging.info(f"Task {task_id} completed successfully.")
            return {"task_id": task_id, "status": "completed", "data": result_data}

        except Exception as e:
            logging.error(f"Error during Reddit scraping orchestration for client {client_id}, agent {agent_id}: {e}")
            if task_id:
                await self.command_bus.dispatch(
                    UpdateTaskStatusCommand(
                        task_id=task_id,
                        status="failed",
                        result_data={"error": str(e)}
                    )
                )
            return {"task_id": task_id, "status": "failed", "error": str(e)}

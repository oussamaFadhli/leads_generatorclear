from app.core.cqrs import CommandHandler
from app.commands.reddit_post_commands import CreateRedditPostCommand, UpdateRedditPostCommand, DeleteRedditPostCommand
from app.repositories import RedditPostRepository
from app.models.models import RedditPost
from typing import Optional

class CreateRedditPostCommandHandler(CommandHandler[CreateRedditPostCommand]):
    def __init__(self, reddit_post_repo: RedditPostRepository):
        self.reddit_post_repo = reddit_post_repo

    async def handle(self, command: CreateRedditPostCommand) -> RedditPost:
        reddit_post_data = command.model_dump()
        return await self.reddit_post_repo.create(reddit_post_data)

class UpdateRedditPostCommandHandler(CommandHandler[UpdateRedditPostCommand]):
    def __init__(self, reddit_post_repo: RedditPostRepository):
        self.reddit_post_repo = reddit_post_repo

    async def handle(self, command: UpdateRedditPostCommand) -> Optional[RedditPost]:
        reddit_post = await self.reddit_post_repo.get(command.reddit_post_id)
        if not reddit_post:
            return None
        update_data = command.model_dump(exclude_unset=True)
        return await self.reddit_post_repo.update(reddit_post, update_data)

class DeleteRedditPostCommandHandler(CommandHandler[DeleteRedditPostCommand]):
    def __init__(self, reddit_post_repo: RedditPostRepository):
        self.reddit_post_repo = reddit_post_repo

    async def handle(self, command: DeleteRedditPostCommand) -> bool:
        reddit_post = await self.reddit_post_repo.get(command.reddit_post_id)
        if not reddit_post:
            return False
        await self.reddit_post_repo.delete(reddit_post)
        return True

from app.core.cqrs import CommandHandler
from app.commands.reddit_comment_commands import CreateRedditCommentCommand, UpdateRedditCommentCommand, DeleteRedditCommentCommand
from app.repositories import RedditCommentRepository
from app.models.models import RedditComment
from typing import Optional

class CreateRedditCommentCommandHandler(CommandHandler[CreateRedditCommentCommand]):
    def __init__(self, reddit_comment_repo: RedditCommentRepository):
        self.reddit_comment_repo = reddit_comment_repo

    async def handle(self, command: CreateRedditCommentCommand) -> RedditComment:
        comment_data = command.model_dump()
        return await self.reddit_comment_repo.create(comment_data)

class UpdateRedditCommentCommandHandler(CommandHandler[UpdateRedditCommentCommand]):
    def __init__(self, reddit_comment_repo: RedditCommentRepository):
        self.reddit_comment_repo = reddit_comment_repo

    async def handle(self, command: UpdateRedditCommentCommand) -> Optional[RedditComment]:
        comment = await self.reddit_comment_repo.get(command.reddit_comment_id)
        if not comment:
            return None
        update_data = command.model_dump(exclude_unset=True)
        return await self.reddit_comment_repo.update(comment, update_data)

class DeleteRedditCommentCommandHandler(CommandHandler[DeleteRedditCommentCommand]):
    def __init__(self, reddit_comment_repo: RedditCommentRepository):
        self.reddit_comment_repo = reddit_comment_repo

    async def handle(self, command: DeleteRedditCommentCommand) -> bool:
        comment = await self.reddit_comment_repo.get(command.reddit_comment_id)
        if not comment:
            return False
        await self.reddit_comment_repo.delete(comment)
        return True

import logging
import time
import random
import praw
from app.schemas import schemas
from app.services.reddit import auth_service, account_service
from app.core.cqrs import CommandBus, QueryBus
from app.queries.reddit_post_queries import GetRedditPostByIdQuery
from app.commands.reddit_post_commands import UpdateRedditPostCommand
from app.queries.reddit_comment_queries import GetRedditCommentByIdQuery
from app.commands.reddit_comment_commands import UpdateRedditCommentCommand
from app.queries.lead_queries import CheckIfAlreadyPostedToSubredditQuery

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def post_generated_reddit_post(post_id: int, command_bus: CommandBus, query_bus: QueryBus):
    """
    Post generated content to Reddit with extensive anti-spam measures.
    ONLY posts once per subreddit per lead.
    """
    logging.info(f"Attempting to post generated Reddit post for Post ID: {post_id}")
    reddit = auth_service.get_reddit_instance()
    if not reddit:
        return
    
    if not account_service.check_account_health(reddit):
        logging.error("Account health check failed. Aborting post.")
        return

    db_post = await query_bus.dispatch(GetRedditPostByIdQuery(reddit_post_id=post_id))
    if not db_post:
        logging.error(f"Reddit Post with ID {post_id} not found.")
        return
    
    if not db_post.generated_title or not db_post.generated_content:
        logging.error(f"Post ID {post_id} does not have generated content to post.")
        return
    
    if not db_post.ai_generated:
        logging.warning(f"Post ID {post_id} is not marked as AI-generated. Skipping posting.")
        return
    
    if db_post.is_posted:
        logging.warning(f"Post ID {post_id} is already marked as posted. Skipping duplicate post.")
        return
    
    # If a posted_url already exists, consider the post as already made and update is_posted if necessary
    if db_post.posted_url and not db_post.is_posted:
        logging.info(f"Post ID {post_id} has an existing posted_url: {db_post.posted_url}. Marking as posted.")
        post_update_schema = schemas.RedditPostUpdate(
            title=db_post.title,
            content=db_post.content,
            score=db_post.score,
            num_comments=db_post.num_comments,
            author=db_post.author,
            url=db_post.url,
            generated_title=db_post.generated_title,
            generated_content=db_post.generated_content,
            is_posted=True,
            ai_generated=db_post.ai_generated,
            posted_url=db_post.posted_url
        )
        update_command = UpdateRedditPostCommand(
            reddit_post_id=post_id,
            is_posted=True,
            posted_url=db_post.posted_url
        )
        await command_bus.dispatch(update_command)
        logging.info(f"Post ID {post_id} updated to is_posted=True based on existing posted_url.")
        return # Abort further posting attempts as it's already considered posted

    # Define test subreddits for development/testing purposes
    TEST_SUBREDDITS = ["testingground4bots"]
    
    # Use test subreddits if in a testing environment, otherwise use subreddits from the database
    # For now, we will always use the test subreddits as per the task request.
    # In a production environment, this logic would be conditional (e.g., based on an environment variable).
    target_subreddits = TEST_SUBREDDITS 
    
    if not target_subreddits:
        logging.warning(f"Post ID {post_id} has no target subreddits defined. Skipping posting.")
        return

    posted_successfully = False

    for target_subreddit in target_subreddits:
        # Check if this specific post (lead_id and generated_title) has already been posted to this target_subreddit
        already_posted = await query_bus.dispatch(CheckIfAlreadyPostedToSubredditQuery(
            lead_id=db_post.lead_id,
            generated_title=db_post.generated_title,
            subreddit_name=target_subreddit
        ))
        if already_posted:
            logging.info(f"Post ID {post_id} (title: '{db_post.generated_title}') already posted to r/{target_subreddit}. Skipping.")
            continue

        delay = 60 # 1 minute delay
        logging.info(f"Waiting {delay:.1f} seconds before posting to r/{target_subreddit} (anti-spam delay)...")
        time.sleep(delay)

        try:
            subreddit = reddit.subreddit(target_subreddit)
            
            submission = None
            comment = None

            if db_post.url and 'comments' in db_post.url:
                try:
                    submission_id = db_post.url.split('/comments/')[1].split('/')[0]
                    submission_to_comment = reddit.submission(id=submission_id)
                    
                    time.sleep(random.uniform(5, 15))
                    
                    comment = submission_to_comment.reply(db_post.generated_content)
                    logging.info(f"Successfully posted comment to r/{target_subreddit} on post: {db_post.title}")
                    logging.info(f"Comment ID: {comment.id}")
                    
                except Exception as e:
                    logging.error(f"Failed to post as comment to r/{target_subreddit}, trying as new post: {e}")
                    # If commenting fails, try posting as a new submission
                    submission = subreddit.submit(
                        db_post.generated_title, 
                        selftext=db_post.generated_content
                    )
                    logging.info(f"Successfully posted to r/{target_subreddit}: '{db_post.generated_title}'")
                    logging.info(f"Submission ID: {submission.id}")
            else:
                submission = subreddit.submit(
                    db_post.generated_title, 
                    selftext=db_post.generated_content
                )
                logging.info(f"Successfully posted to r/{target_subreddit}: '{db_post.generated_title}'")
                logging.info(f"Submission ID: {submission.id}")
            
            time.sleep(random.uniform(10, 20))

            update_command = UpdateRedditPostCommand(
                reddit_post_id=post_id,
                is_posted=True,
                posted_url=f"https://www.reddit.com{comment.permalink}" if comment else f"https://www.reddit.com{submission.permalink}",
                subreddits=db_post.subreddits + [target_subreddit] # Add the successfully posted subreddit
            )
            await command_bus.dispatch(update_command)
            posted_successfully = True
            
        except Exception as e:
            logging.error(f"Failed to post to r/{target_subreddit} for Post ID {post_id}: {e}")
    
    if not posted_successfully:
        logging.warning(f"Post ID {post_id} was not successfully posted to any target subreddit.")

async def post_reddit_comment_reply(
    reddit: praw.Reddit, 
    parent_comment_id: str, 
    reply_content: str, 
    command_bus: CommandBus, 
    query_bus: QueryBus,
    reddit_comment_db_id: int
):
    """
    Posts a reply to a specific Reddit comment.
    """
    logging.info(f"Attempting to post reply to Reddit comment ID: {parent_comment_id}")
    
    try:
        parent_comment = reddit.comment(id=parent_comment_id)
        
        time.sleep(random.uniform(5, 15)) # Anti-spam delay
        
        reply = parent_comment.reply(reply_content)
        logging.info(f"Successfully posted reply to comment ID {parent_comment_id}. Reply ID: {reply.id}")
        
        update_command = UpdateRedditCommentCommand(
            reddit_comment_id=reddit_comment_db_id,
            is_replied=True,
            reply_permalink=reply.permalink
        )
        await command_bus.dispatch(update_command)
        return True
    except Exception as e:
        logging.error(f"Failed to post reply to comment ID {parent_comment_id}. Reason: {e}")
        return False

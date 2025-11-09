from pydantic import BaseModel, Field

class GeneratedPost(BaseModel):
    original_post_url: str = Field(description="The URL of the original Reddit post that inspired this generated post.")
    title: str = Field(description="The generated title for the new Reddit post.")
    content: str = Field(description="The generated content for the new Reddit post, written in a human-like tone.")

class GeneratedPostsResult(BaseModel):
    generated_posts: list[GeneratedPost]

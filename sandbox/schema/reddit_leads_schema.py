from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Feature(BaseModel):
    name: str
    desc: str

class PricingPlan(BaseModel):
    plan_name: str
    price: str
    features: List[str]
    link: str

class RedditPost(BaseModel):
    title: str
    content: str
    score: int
    num_comments: int
    author: str
    url: str
    subreddit: str

class ScoredRedditPost(RedditPost):
    lead_score: float = Field(..., description="A numerical score indicating the potential of this post to generate a lead for Trucking88.")
    score_justification: str = Field(..., description="A brief explanation of why this post received its score, highlighting its relevance to Trucking88's features and target audience.")

class RedditLeadsAnalysisResult(BaseModel):
    top_leads: List[ScoredRedditPost] = Field(..., description="A list of the top 10 Reddit posts identified as potential leads, including their scores and justifications.")

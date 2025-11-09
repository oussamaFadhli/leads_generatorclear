from pydantic import BaseModel, Field
from typing import List, Dict

class Competitor(BaseModel):
    name: str = Field(description="Name of the competitor.")
    strengths: List[str] = Field(description="List of strengths of the competitor.")
    weaknesses: List[str] = Field(description="List of weaknesses of the competitor.")

class LeadsSearchResult(BaseModel):
    competitors: List[Competitor] = Field(description="List of famous competitors for the SaaS project, including their strengths and weaknesses.")
    related_subreddits: List[str] = Field(description="List of best subreddits related to the SaaS project's interests.")

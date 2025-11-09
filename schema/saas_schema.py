from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Feature(BaseModel):
    name: str
    description: str = Field(alias="desc")

class Pricing(BaseModel):
    # Assuming pricing can be a list of various structures,
    # for now, we'll keep it flexible.
    # If a more specific structure is known, it can be refined.
    plan_name: str
    price: str
    features: List[str] = []
    link: Optional[str] = None

class SaaSInfo(BaseModel):
    name: str
    one_liner: str
    features: List[Feature]
    pricing: List[Pricing]
    target_segments: List[str]

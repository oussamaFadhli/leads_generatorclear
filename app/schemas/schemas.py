from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum
import json
from datetime import datetime # Import datetime

# Feature Schemas
class FeatureBase(BaseModel):
    name: str
    description: str

class FeatureCreate(FeatureBase):
    pass

class Feature(FeatureBase):
    id: int
    saas_info_id: int

    class Config:
        from_attributes = True

# Pricing Plan Schemas
class PricingPlanBase(BaseModel):
    plan_name: str
    price: str
    features: List[str] # Expecting a list of strings from scraper
    link: Optional[str] = None


class PricingPlanCreate(PricingPlanBase):
    pass

class PricingPlan(PricingPlanBase):
    id: int
    saas_info_id: int

    class Config:
        from_attributes = True

# SaaS Info Schemas
class SaaSInfoBase(BaseModel):
    name: str
    one_liner: str
    target_segments: Optional[List[str]] = None # Made optional for testing simplified scraper


class SaaSInfoCreate(SaaSInfoBase):
    features: Optional[List[FeatureCreate]] = None
    pricing: Optional[List[PricingPlanCreate]] = None
    target_segments: Optional[List[str]] = None

class SaaSInfo(SaaSInfoBase):
    id: int
    features: List[Feature] = []
    pricing: List[PricingPlan] = []

    class Config:
        from_attributes = True

# Reddit Post Schemas
class RedditPostBase(BaseModel):
    title: str
    content: str
    score: int
    num_comments: int


    # --- Basic Feature & Pricing Schemas (compatible with existing code) ---
class FeatureBase(BaseModel):
        name: str
        description: str = Field(alias="desc")

        model_config = {"populate_by_name": True}

class FeatureCreate(FeatureBase):
        pass

class Feature(FeatureBase):
        id: int
        saas_info_id: int

        model_config = {"from_attributes": True}


class PricingPlanBase(BaseModel):
        plan_name: str
        price: str
        features: List[str] = Field(default_factory=list)
        link: Optional[str] = None

class PricingPlanCreate(PricingPlanBase):
        pass

class PricingPlan(PricingPlanBase):
        id: int
        saas_info_id: int

        model_config = {"from_attributes": True}


    # --- Contact & Social ---
class ContactInfo(BaseModel):
        email: Optional[str] = None
        phone: Optional[str] = None
        address: Optional[str] = None


class SocialLinks(BaseModel):
        linkedin: Optional[str] = None
        twitter: Optional[str] = None
        facebook: Optional[str] = None


    # --- Strategic Models ---
class BusinessProfile(BaseModel):
        business_type: str
        industry: str
        geo: List[str] = Field(default_factory=list)
        main_offers: List[str] = Field(default_factory=list)
        price_points: Dict[str, str] = Field(default_factory=dict)
        business_goals: List[str] = Field(default_factory=list)


class ICPProfile(BaseModel):
        segment: str
        pains: List[str] = Field(default_factory=list)
        goals: List[str] = Field(default_factory=list)
        objections: List[str] = Field(default_factory=list)
        channels: List[str] = Field(default_factory=list)
        buying_triggers: List[str] = Field(default_factory=list)
        negative_signals: List[str] = Field(default_factory=list)
        confidence_score: int


class OfferBreakdown(BaseModel):
        offer_name: str
        benefits: List[str] = Field(default_factory=list)
        proof: List[str] = Field(default_factory=list)
        guarantees: List[str] = Field(default_factory=list)
        urgency: List[str] = Field(default_factory=list)
        pain_points: List[str] = Field(default_factory=list)
        objections_handled: List[str] = Field(default_factory=list)


class SocialChannel(str, Enum):
        LINKEDIN = "LinkedIn"
        EMAIL = "Email"
        TWITTER = "Twitter (X)"
        REDDIT = "Reddit"
        FACEBOOK = "Facebook"
        INSTAGRAM = "Instagram"
        TIKTOK = "TikTok"
        YOUTUBE = "YouTube"
        PINTEREST = "Pinterest"
        QUORA = "Quora"
        DISCORD = "Discord"
        SLACK_COMMUNITIES = "Slack Communities"
        PRODUCT_HUNT = "Product Hunt"
        HACKER_NEWS = "Hacker News"
        MEDIUM = "Medium"
        DEV_TO = "Dev.to"


class ChannelMapping(BaseModel):
        primary_channels: List[SocialChannel] = Field(default_factory=list)
        secondary_channels: List[SocialChannel] = Field(default_factory=list)
        forbidden_channels: List[SocialChannel] = Field(default_factory=list)


    # --- Advanced Intelligence Models ---
class PsychologyLanguage(BaseModel):
        primary_objections: List[str] = Field(default_factory=list)
        emotional_triggers: List[str] = Field(default_factory=list)
        problem_vocabulary: List[str] = Field(default_factory=list)
        solution_vocabulary: List[str] = Field(default_factory=list)
        evidence_snippets: List[str] = Field(default_factory=list)


class MarketIntelligence(BaseModel):
        market_size: Optional[str] = None
        growth_rate: Optional[str] = None
        key_trends: List[str] = Field(default_factory=list)
        regulations: List[str] = Field(default_factory=list)
        competitive_intensity: Optional[str] = None
        market_maturity: Optional[str] = None
        confidence_score: int


class CustomerVoice(BaseModel):
        positive_quotes: List[str] = Field(default_factory=list)
        common_praises: List[str] = Field(default_factory=list)
        common_complaints: List[str] = Field(default_factory=list)
        language_patterns: List[str] = Field(default_factory=list)


class BuyerJourneyStage(BaseModel):
        duration_days: Optional[str] = None
        touchpoints: List[str] = Field(default_factory=list)
        objections: List[str] = Field(default_factory=list)
        content_needed: List[str] = Field(default_factory=list)


class BuyerJourney(BaseModel):
        awareness_stage: Optional[BuyerJourneyStage] = None
        consideration_stage: Optional[BuyerJourneyStage] = None
        decision_stage: Optional[BuyerJourneyStage] = None


class DecisionMaker(BaseModel):
        primary_decision_maker: Optional[str] = None
        influencers: List[str] = Field(default_factory=list)
        motivations_by_role: Dict[str, str] = Field(default_factory=dict)
        objections_by_role: Dict[str, str] = Field(default_factory=dict)


class AccountScoring(BaseModel):
        icp_fit_score: Optional[int] = None
        recommended_action: Optional[str] = None
        optimal_contact_window: Optional[str] = None


    # --- SaaS Info Schemas ---
class SaaSInfoBase(BaseModel):
        name: str
        one_liner: str
        target_segments: Optional[List[str]] = Field(default_factory=list)


class SaaSInfoCreate(SaaSInfoBase):
        features: Optional[List[FeatureCreate]] = None
        pricing: Optional[List[PricingPlanCreate]] = None
        detected_technologies: Optional[List[str]] = None
        contact_info: Optional[ContactInfo] = None
        social_links: Optional[SocialLinks] = None
        business_profile: Optional[BusinessProfile] = None
        icp_profiles: Optional[List[ICPProfile]] = None
        offer_breakdowns: Optional[List[OfferBreakdown]] = None
        channel_mapping: Optional[ChannelMapping] = None
        psychology_language: Optional[PsychologyLanguage] = None
        market_intelligence: Optional[MarketIntelligence] = None
        customer_voice: Optional[CustomerVoice] = None
        buyer_journey: Optional[BuyerJourney] = None
        decision_makers: Optional[DecisionMaker] = None
        account_scoring: Optional[AccountScoring] = None


class SaaSInfo(SaaSInfoBase):
        id: int
        features: List[Feature] = Field(default_factory=list)
        pricing: List[PricingPlan] = Field(default_factory=list)
        detected_technologies: List[str] = Field(default_factory=list)
        contact_info: Optional[ContactInfo] = None
        social_links: Optional[SocialLinks] = None
        business_profile: Optional[BusinessProfile] = None
        icp_profiles: List[ICPProfile] = Field(default_factory=list)
        offer_breakdowns: List[OfferBreakdown] = Field(default_factory=list)
        channel_mapping: Optional[ChannelMapping] = None
        psychology_language: Optional[PsychologyLanguage] = None
        market_intelligence: Optional[MarketIntelligence] = None
        customer_voice: Optional[CustomerVoice] = None
        buyer_journey: Optional[BuyerJourney] = None
        decision_makers: Optional[DecisionMaker] = None
        account_scoring: Optional[AccountScoring] = None

        model_config = {"from_attributes": True}

    # --- Reddit/Post/Lead schemas (kept minimal to avoid regressions) ---
class RedditPostBase(BaseModel):
        title: str
        content: str
        score: int
        num_comments: int
        author: str
        url: str
        subreddits: Optional[List[str]] = None


class RedditPostCreate(RedditPostBase):
        pass


class RedditPostUpdate(RedditPostBase):
        subreddits: Optional[List[str]] = Field(default_factory=list)
        lead_score: Optional[float] = None
        score_justification: Optional[str] = None
        generated_title: Optional[str] = None
        generated_content: Optional[str] = None
        is_posted: Optional[bool] = False
        ai_generated: Optional[bool] = False
        posted_url: Optional[str] = None


class RedditPost(RedditPostBase):
        id: int
        lead_id: int
        lead_score: Optional[float] = None
        score_justification: Optional[str] = None
        generated_title: Optional[str] = None
        generated_content: Optional[str] = None
        posted_url: Optional[str] = None
        is_posted: bool = False
        ai_generated: bool = False

        model_config = {"from_attributes": True}


class ScoredRedditPostList(BaseModel):
        posts: List[RedditPostUpdate]


class GeneratedPostContent(BaseModel):
        title: str
        content: str


class RedditCommentBase(BaseModel):
        comment_id: str
        post_id: str
        author: str
        content: str
        score: int
        permalink: str


class RedditCommentCreate(RedditCommentBase):
        pass


class RedditComment(RedditCommentBase):
        id: int
        reddit_post_db_id: int
        generated_reply_content: Optional[str] = None
        is_replied: bool = False
        ai_generated: bool = False

        model_config = {"from_attributes": True}


class GeneratedCommentContent(BaseModel):
        content: str


class LeadBase(BaseModel):
        competitor_name: str
        strengths: List[str] = Field(default_factory=list)
        weaknesses: List[str] = Field(default_factory=list)
        related_subreddits: List[str] = Field(default_factory=list)


class LeadCreate(LeadBase):
        pass


class LeadsCreate(BaseModel):
        leads: List[LeadCreate]


class Lead(LeadBase):
        id: int
        saas_info_id: int
        reddit_posts: List[RedditPost] = Field(default_factory=list)

        model_config = {"from_attributes": True}

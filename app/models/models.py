from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB # Import JSONB for PostgreSQL
import json
from typing import List, Optional
from sqlalchemy.orm import relationship, backref
from app.core.database import Base

class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    saas_info_id = Column(Integer, ForeignKey("saas_info.id", ondelete="CASCADE"))

class PricingPlan(Base):
    __tablename__ = "pricing_plans"
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String, index=True)
    price = Column(String)
    features = Column(JSONB)  # Storing as JSONB
    link = Column(String, nullable=True)
    saas_info_id = Column(Integer, ForeignKey("saas_info.id", ondelete="CASCADE"))

class SaaSInfo(Base):
    __tablename__ = "saas_info"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    one_liner = Column(Text)
    target_segments = Column(JSONB) # Storing as JSONB

    @property
    def target_segments_list(self) -> Optional[List[str]]:
        return self.target_segments

    features = relationship(
        "Feature",
        backref="saas_info",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    pricing = relationship(
        "PricingPlan",
        backref="saas_info",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    leads = relationship(
        "Lead",
        backref="saas_info",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    competitor_name = Column(String, index=True)
    strengths = Column(JSONB) # Storing as JSONB
    weaknesses = Column(JSONB) # Storing as JSONB
    related_subreddits = Column(JSONB) # Storing as JSONB
    saas_info_id = Column(Integer, ForeignKey("saas_info.id", ondelete="CASCADE"))
    reddit_posts = relationship(
        "RedditPost",
        backref="lead",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @property
    def strengths_list(self) -> Optional[List[str]]:
        return self.strengths

    @property
    def weaknesses_list(self) -> Optional[List[str]]:
        return self.weaknesses

    @property
    def related_subreddits_list(self) -> Optional[List[str]]:
        return self.related_subreddits

class RedditPost(Base):
    __tablename__ = "reddit_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    score = Column(Integer)
    num_comments = Column(Integer)
    author = Column(String)
    url = Column(String)
    subreddits = Column(JSONB) # Storing as JSONB
    lead_score = Column(Float, nullable=True)
    score_justification = Column(Text, nullable=True)
    generated_title = Column(String, nullable=True)
    generated_content = Column(Text, nullable=True)
    is_posted = Column(Boolean, default=False)
    ai_generated = Column(Boolean, default=False)
    posted_url = Column(String, nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"))

    @property
    def subreddits_list(self) -> List[str]:
        return self.subreddits if self.subreddits is not None else []

class RedditComment(Base):
    __tablename__ = "reddit_comments"
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String, index=True)
    post_id = Column(String) # The Reddit ID of the post this comment belongs to
    author = Column(String)
    content = Column(Text)
    score = Column(Integer)
    permalink = Column(String)
    reddit_post_db_id = Column(Integer, ForeignKey("reddit_posts.id", ondelete="CASCADE")) # Our internal RedditPost ID
    generated_reply_content = Column(Text, nullable=True)
    is_replied = Column(Boolean, default=False)
    ai_generated = Column(Boolean, default=False)

    reddit_post = relationship(
        "RedditPost",
        backref=backref("comments", cascade="all, delete-orphan", lazy="selectin"),
        lazy="selectin"
    )

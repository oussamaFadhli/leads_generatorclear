from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas
import json
from typing import List, Optional

# CRUD for SaaSInfo
def get_saas_info(db: Session, saas_info_id: int):
    return db.query(models.SaaSInfo).filter(models.SaaSInfo.id == saas_info_id).first()

def get_saas_info_by_name(db: Session, name: str):
    return db.query(models.SaaSInfo).filter(models.SaaSInfo.name == name).first()

def get_all_saas_info(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SaaSInfo).offset(skip).limit(limit).all()

def create_saas_info(db: Session, saas_info: schemas.SaaSInfoCreate):
    db_saas_info = models.SaaSInfo(
        name=saas_info.name,
        one_liner=saas_info.one_liner,
        target_segments=saas_info.target_segments
    )
    db.add(db_saas_info)
    db.commit()
    db.refresh(db_saas_info)
    for feature_data in saas_info.features or []:
        db_feature = models.Feature(**feature_data.model_dump(), saas_info_id=db_saas_info.id)
        db.add(db_feature)
    
    for pricing_data in saas_info.pricing or []:
        db_pricing = models.PricingPlan(
            plan_name=pricing_data.plan_name,
            price=pricing_data.price,
            features=pricing_data.features if pricing_data.features is not None else [],
            link=pricing_data.link,
            saas_info_id=db_saas_info.id
        )
        db.add(db_pricing)
    db.commit()
    db.refresh(db_saas_info)
    return db_saas_info

def update_saas_info(db: Session, saas_info_id: int, saas_info: schemas.SaaSInfoCreate):
    db_saas_info = db.query(models.SaaSInfo).filter(models.SaaSInfo.id == saas_info_id).first()
    if db_saas_info:
        db_saas_info.name = saas_info.name
        db_saas_info.one_liner = saas_info.one_liner
        db_saas_info.target_segments = saas_info.target_segments

        # Update features
        db.query(models.Feature).filter(models.Feature.saas_info_id == saas_info_id).delete()
        for feature_data in saas_info.features or []:
            db_feature = models.Feature(**feature_data.model_dump(), saas_info_id=saas_info_id)
            db.add(db_feature)
        
        # Update pricing plans
        db.query(models.PricingPlan).filter(models.PricingPlan.saas_info_id == saas_info_id).delete()
        for pricing_data in saas_info.pricing or []:
            db_pricing = models.PricingPlan(
                plan_name=pricing_data.plan_name,
                price=pricing_data.price,
                features=pricing_data.features if pricing_data.features is not None else [],
                link=pricing_data.link,
                saas_info_id=saas_info_id
            )
            db.add(db_pricing)

        db.commit()
        db.refresh(db_saas_info)
    return db_saas_info

def delete_saas_info(db: Session, saas_info_id: int):
    db_saas_info = db.query(models.SaaSInfo).filter(models.SaaSInfo.id == saas_info_id).first()
    if db_saas_info:
        db.delete(db_saas_info)
        db.commit()
    return db_saas_info

# CRUD for Leads
def get_lead(db: Session, lead_id: int):
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()

def get_leads_for_saas_info(db: Session, saas_info_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Lead).filter(models.Lead.saas_info_id == saas_info_id).offset(skip).limit(limit).all()

def create_lead(db: Session, lead: schemas.LeadCreate, saas_info_id: int):
    strengths_json = json.dumps(lead.strengths) if lead.strengths is not None else None
    weaknesses_json = json.dumps(lead.weaknesses) if lead.weaknesses is not None else None
    related_subreddits_json = json.dumps(lead.related_subreddits) if lead.related_subreddits is not None else None
    db_lead = models.Lead(
        competitor_name=lead.competitor_name,
        strengths=strengths_json,
        weaknesses=weaknesses_json,
        related_subreddits=related_subreddits_json,
        saas_info_id=saas_info_id
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def delete_lead(db: Session, lead_id: int):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if db_lead:
        db.delete(db_lead)
        db.commit()
    return db_lead

# CRUD for Reddit Posts
def get_reddit_post(db: Session, post_id: int):
    return db.query(models.RedditPost).filter(models.RedditPost.id == post_id).first()

def get_reddit_posts_for_lead(db: Session, lead_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.RedditPost).filter(models.RedditPost.lead_id == lead_id).offset(skip).limit(limit).all()

def create_reddit_post(db: Session, post: schemas.RedditPostCreate, lead_id: int):
    # Convert subreddits list to JSON string for storage
    subreddits_json = json.dumps(post.subreddits) if post.subreddits is not None else None
    
    db_post = models.RedditPost(
        title=post.title,
        content=post.content,
        score=post.score,
        num_comments=post.num_comments,
        author=post.author,
        url=post.url,
        subreddits=subreddits_json, # Save as JSON string
        lead_id=lead_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_reddit_post(db: Session, post_id: int, post_update: schemas.RedditPostUpdate):
    db_post = db.query(models.RedditPost).filter(models.RedditPost.id == post_id).first()
    if db_post:
        # Use model_dump without exclude_unset for subreddits to ensure it's always present
        # and handle other fields with exclude_unset=True
        update_data = post_update.model_dump(exclude_unset=True)
        
        # Explicitly handle subreddits to ensure it's converted to JSON string
        # and is not excluded if it's an empty list.
        if 'subreddits' in post_update.model_fields_set: # Check if subreddits was explicitly provided
            db_post.subreddits = json.dumps(post_update.subreddits) if post_update.subreddits is not None else json.dumps([])
            if 'subreddits' in update_data: # Remove from update_data if it was included by model_dump
                del update_data['subreddits']
        
        for key, value in update_data.items():
            setattr(db_post, key, value)
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
    return db_post

def delete_reddit_post(db: Session, post_id: int):
    db_post = db.query(models.RedditPost).filter(models.RedditPost.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post

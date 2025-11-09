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
    target_segments_json = json.dumps(saas_info.target_segments) if saas_info.target_segments is not None else None
    db_saas_info = models.SaaSInfo(
        name=saas_info.name,
        one_liner=saas_info.one_liner,
        target_segments=target_segments_json
    )
    db.add(db_saas_info)
    db.commit()
    db.refresh(db_saas_info)

    for feature_data in saas_info.features:
        db_feature = models.Feature(**feature_data.model_dump(), saas_info_id=db_saas_info.id)
        db.add(db_feature)
    
    for pricing_data in saas_info.pricing:
        pricing_features_json = json.dumps(pricing_data.features) if pricing_data.features is not None else None
        db_pricing = models.PricingPlan(
            plan_name=pricing_data.plan_name,
            price=pricing_data.price,
            features=pricing_features_json,
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
        db_saas_info.target_segments = json.dumps(saas_info.target_segments) if saas_info.target_segments is not None else None

        # Update features
        db.query(models.Feature).filter(models.Feature.saas_info_id == saas_info_id).delete()
        for feature_data in saas_info.features:
            db_feature = models.Feature(**feature_data.model_dump(), saas_info_id=saas_info_id)
            db.add(db_feature)
        
        # Update pricing plans
        db.query(models.PricingPlan).filter(models.PricingPlan.saas_info_id == saas_info_id).delete()
        for pricing_data in saas_info.pricing:
            pricing_features_json = json.dumps(pricing_data.features) if pricing_data.features is not None else None
            db_pricing = models.PricingPlan(
                plan_name=pricing_data.plan_name,
                price=pricing_data.price,
                features=pricing_features_json,
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
    related_subreddits_json = json.dumps(lead.related_subreddits) if lead.related_subreddits is not None else None
    db_lead = models.Lead(
        competitor_name=lead.competitor_name,
        strength=lead.strength,
        weakness=lead.weakness,
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
    db_post = models.RedditPost(**post.model_dump(), lead_id=lead_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_reddit_post(db: Session, post_id: int, post_update: schemas.RedditPostUpdate):
    db_post = db.query(models.RedditPost).filter(models.RedditPost.id == post_id).first()
    if db_post:
        update_data = post_update.model_dump(exclude_unset=True)
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

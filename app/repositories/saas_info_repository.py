from typing import Optional, Dict, Any, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import SaaSInfo, Feature, PricingPlan
from app.repositories.base import BaseRepository


class SaaSInfoRepository(BaseRepository[SaaSInfo]):
    def __init__(self, db: AsyncSession):
        super().__init__(SaaSInfo, db)

    async def get_by_name(self, name: str) -> Optional[SaaSInfo]:
        result = await self.db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()

    async def create(self, obj_in: Dict[str, Any]) -> SaaSInfo:
        features: Optional[List[Dict[str, Any]]] = obj_in.pop("features", None)
        pricing: Optional[List[Dict[str, Any]]] = obj_in.pop("pricing", None)

        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        if features:
            for f in features:
                f_obj = Feature(**f, saas_info_id=db_obj.id)
                self.db.add(f_obj)

        if pricing:
            for p in pricing:
                p_obj = PricingPlan(**p, saas_info_id=db_obj.id)
                self.db.add(p_obj)

        if features or pricing:
            await self.db.commit()
            await self.db.refresh(db_obj)

        return db_obj

    async def update(self, db_obj: SaaSInfo, obj_in: Dict[str, Any]) -> SaaSInfo:
        # Handle nested children and JSON fields
        features = obj_in.pop("features", None)
        pricing = obj_in.pop("pricing", None)

        for key, value in obj_in.items():
            setattr(db_obj, key, value)

        # delete and recreate features/pricing if provided
        if features is not None:
            await self.db.execute(delete(Feature).where(Feature.saas_info_id == db_obj.id))
            for f in features:
                f_obj = Feature(**f, saas_info_id=db_obj.id)
                self.db.add(f_obj)

        if pricing is not None:
            await self.db.execute(delete(PricingPlan).where(PricingPlan.saas_info_id == db_obj.id))
            for p in pricing:
                p_obj = PricingPlan(**p, saas_info_id=db_obj.id)
                self.db.add(p_obj)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

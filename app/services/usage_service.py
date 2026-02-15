from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.usage import Usage

class UsageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def increment_usage(self, org_id: str, metric_name: str, amount: int = 1):
        # Check if metric exists
        result = await self.db.execute(select(Usage).where(
            Usage.organization_id == org_id,
            Usage.metric_name == metric_name
        ))
        usage = result.scalars().first()
        
        if usage:
            usage.value += amount
        else:
            usage = Usage(
                organization_id=org_id,
                metric_name=metric_name,
                value=amount
            )
        
        self.db.add(usage)
        await self.db.commit()

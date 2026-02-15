from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_org
from app.models.organization import Organization
from app.schemas.job import JobResponse
from app.services.job_service import JobService
from app.core.response import StandardResponse

router = APIRouter()

@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = JobService(db)
    job = await service.get_job(job_id, current_org.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return StandardResponse.success({
        "id": job.id,
        "organization_id": job.organization_id,
        "type": job.type,
        "status": job.status,
        "result_path": job.result_path,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    })

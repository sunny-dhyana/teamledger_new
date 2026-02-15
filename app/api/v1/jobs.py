from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
from app.core.database import get_db
from app.core.deps import get_current_org, get_request_context
from app.core.permissions import RequestContext
from app.models.organization import Organization
from app.schemas.job import JobResponse
from app.services.job_service import JobService
from app.core.response import StandardResponse

router = APIRouter()

@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = JobService(db)
    job = await service.get_job(job_id, context.org_id)
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

@router.get("/{job_id}/download")
async def download_job_result(
    job_id: str,
    path: Optional[str] = Query(None),
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = JobService(db)
    job = await service.get_job(job_id, context.org_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")

    file_path = path if path else job.result_path

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Export file not found")

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=f"export_{job_id}.json"
    )

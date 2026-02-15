from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_org, get_request_context
from app.core.permissions import RequestContext
from app.models.organization import Organization
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService
from app.services.usage_service import UsageService
from app.services.job_service import JobService
from app.services.import_service import ImportService
from app.schemas.job import JobResponse
from fastapi import BackgroundTasks
from app.core.response import StandardResponse

router = APIRouter()

@router.post("/")
async def create_project(
    project_in: ProjectCreate,
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    project_service = ProjectService(db)
    project = await project_service.create_project(current_org.id, project_in)

    # Track usage
    usage_service = UsageService(db)
    await usage_service.increment_usage(current_org.id, "projects_created")

    return StandardResponse.success({
        "id": project.id,
        "organization_id": project.organization_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    })

@router.get("/")
async def list_projects(
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    project_service = ProjectService(db)
    projects = await project_service.get_projects(context.org_id)
    return StandardResponse.success([{
        "id": p.id,
        "organization_id": p.organization_id,
        "name": p.name,
        "description": p.description,
        "status": p.status,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat()
    } for p in projects])

@router.get("/{project_id}")
async def get_project(
    project_id: str,
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, context.org_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return StandardResponse.success({
        "id": project.id,
        "organization_id": project.organization_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    })

@router.put("/{project_id}")
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    project_service = ProjectService(db)
    project = await project_service.update_project(project_id, context.org_id, project_in)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return StandardResponse.success({
        "id": project.id,
        "organization_id": project.organization_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    })

@router.post("/{project_id}/export")
async def export_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    current_org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Verify project exists
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id, current_org.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job_service = JobService(db)
    job = await job_service.create_export_job(current_org.id)

    background_tasks.add_task(JobService.process_export, job.id, current_org.id)

    return StandardResponse.success({
        "id": job.id,
        "organization_id": job.organization_id,
        "type": job.type,
        "status": job.status,
        "result_path": job.result_path,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    })

@router.post("/import")
async def import_project(
    data: Dict[str, Any] = Body(...),
    context: RequestContext = Depends(get_request_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    context.permissions.require_write()

    import_service = ImportService(db)
    project = await import_service.import_project(
        org_id=context.org_id,
        data=data,
        created_by=context.user_id
    )

    return StandardResponse.success({
        "id": project.id,
        "organization_id": project.organization_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "message": "Project imported successfully"
    })

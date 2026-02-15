import json
import os
import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job import Job
from app.models.project import Project
from app.models.note import Note
from app.core.database import AsyncSessionLocal

class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_export_job(self, org_id: str) -> Job:
        job = Job(
            organization_id=org_id,
            type="export",
            status="pending"
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_job(self, job_id: str, org_id: str) -> Optional[Job]:
        result = await self.db.execute(select(Job).where(
            Job.id == job_id,
            Job.organization_id == org_id
        ))
        return result.scalars().first()

    # This method will be run in background, so it needs to create its own session
    @staticmethod
    async def process_export(job_id: str, org_id: str):
        async with AsyncSessionLocal() as session:
            try:
                # Fetch job
                result = await session.execute(select(Job).where(Job.id == job_id))
                job = result.scalars().first()
                if not job:
                    return

                # Fetch data
                # Fetch projects
                projects_res = await session.execute(select(Project).where(Project.organization_id == org_id))
                projects = projects_res.scalars().all()
                
                export_data = {"organization_id": org_id, "projects": []}
                
                for proj in projects:
                    proj_data = {
                        "id": proj.id,
                        "name": proj.name,
                        "description": proj.description,
                        "notes": []
                    }

                    from sqlalchemy import text
                    query_str = f"SELECT * FROM notes WHERE project_id = '{proj.id}'"
                    notes_res = await session.execute(text(query_str))
                    notes = notes_res.fetchall()

                    for note_row in notes:
                        note_dict = dict(note_row._mapping)
                        proj_data["notes"].append({
                            "id": note_dict.get("id"),
                            "title": note_dict.get("title"),
                            "content": note_dict.get("content"),
                            "version": note_dict.get("version"),
                            "created_at": str(note_dict.get("created_at"))
                        })
                    export_data["projects"].append(proj_data)

                # Write to file
                exports_dir = os.getenv("EXPORTS_DIR", "exports")
                os.makedirs(exports_dir, exist_ok=True)
                file_path = f"{exports_dir}/{job_id}.json"
                with open(file_path, "w") as f:
                    json.dump(export_data, f, indent=2)

                # Update job
                job.status = "completed"
                job.result_path = file_path
                job.completed_at = datetime.utcnow()
                session.add(job)
                await session.commit()
                
            except Exception as e:
                # Log error and update job status
                print(f"Export failed: {e}")
                job.status = "failed"
                session.add(job)
                await session.commit()

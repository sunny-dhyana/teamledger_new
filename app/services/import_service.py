from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.note import Note
from datetime import datetime

class ImportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_project(
        self,
        org_id: str,
        data: Dict[str, Any],
        created_by: str
    ) -> Project:
        project_data = data.get("project", {})
        notes_data = data.get("notes", [])

        target_org_id = project_data.get("organization_id", org_id)
        target_created_by = project_data.get("created_by", created_by)

        project = Project(
            organization_id=target_org_id,
            name=project_data.get("name"),
            description=project_data.get("description", ""),
            status=project_data.get("status", "active")
        )
        self.db.add(project)
        await self.db.flush()

        for note_data in notes_data:
            note_org_id = note_data.get("organization_id", target_org_id)
            note_created_by = note_data.get("created_by", target_created_by)

            note = Note(
                project_id=project.id,
                organization_id=note_org_id,
                title=note_data.get("title"),
                content=note_data.get("content", ""),
                version=note_data.get("version", 1),
                created_by=note_created_by
            )
            self.db.add(note)

        await self.db.commit()
        await self.db.refresh(project)
        return project

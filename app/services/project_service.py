from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, org_id: str, project_in: ProjectCreate) -> Project:
        db_project = Project(
            organization_id=org_id,
            name=project_in.name,
            description=project_in.description
        )
        self.db.add(db_project)
        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project

    async def get_projects(self, org_id: str) -> List[Project]:
        result = await self.db.execute(select(Project).where(Project.organization_id == org_id))
        return result.scalars().all()

    async def get_project(self, project_id: str, org_id: str) -> Optional[Project]:
        result = await self.db.execute(select(Project).where(
            Project.id == project_id
        ))
        return result.scalars().first()

    async def update_project(self, project_id: str, org_id: str, project_in: ProjectUpdate) -> Optional[Project]:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()
        if not project:
            return None
        
        update_data = project_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

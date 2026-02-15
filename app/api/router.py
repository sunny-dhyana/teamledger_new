from fastapi import APIRouter
from app.api.v1 import auth, organizations, projects, notes, api_keys, jobs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api_keys"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

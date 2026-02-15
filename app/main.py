from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import os
from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router
from app.core.response import StandardResponse
from app import models  # Ensure all models are imported

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse.error(exc.detail)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=StandardResponse.error(str(exc))
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=StandardResponse.error("Internal server error")
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
frontend_path = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/health")
async def health_check():
    return {"status": "ok_v2"}

# Catch-all route for SPA
@app.get("/{rest_of_path:path}")
async def catch_all(rest_of_path: str):
    # If the path starts with api/, let it fall through to 404 handled by router or return 404 here
    if rest_of_path.startswith("api/"):
         return {"detail": "Not Found"}
    
    # Check if file exists in dist (for icons, favicon etc)
    local_path = os.path.join(frontend_path, rest_of_path)
    if os.path.isfile(local_path):
        return FileResponse(local_path)

    # Return index.html for all other frontend routes
    return FileResponse(os.path.join(frontend_path, "index.html"))

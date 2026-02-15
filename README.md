# TeamLedger

A lightweight multi-tenant SaaS platform for managing organizations, projects, and notes with a modern React frontend.

## Features

- **Multi-tenancy**: Organization-based data isolation.
- **Authentication**: JWT-based auth with role-based access control (RBAC).
- **Projects & Notes**: Manage projects and collaborate on notes.
- **Note Sharing**: Generate public shareable links for notes.
- **API Keys**: Secure API access for organizations.
- **Background Tasks**: Async export of project data.
- **Usage Tracking**: Monitor organization usage limits.
- **Modern UI**: React + TypeScript + Tailwind CSS frontend.

## Tech Stack

### Backend
- **Python 3.12+**
- **FastAPI**
- **SQLAlchemy 2.0 (Async)**
- **SQLite** (default) / PostgreSQL (supported)
- **Pydantic v2**

### Frontend
- **React 18**
- **TypeScript**
- **Vite**
- **React Router**
- **Axios**
- **Zustand** (State Management)
- **Tailwind CSS**

## Quick Start

### Development Mode (Frontend + Backend Separate)

1.  **Install backend dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the backend**:
    ```bash
    uvicorn app.main:app --reload
    ```
    Backend will run on [http://localhost:8000](http://localhost:8000)

3.  **Install frontend dependencies**:
    ```bash
    cd frontend
    npm install
    ```

4.  **Run the frontend dev server**:
    ```bash
    npm run dev
    ```
    Frontend will run on [http://localhost:3000](http://localhost:3000)

5.  **Access the application**:
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Production Mode (Serve from Same Port)

1.  **Build the frontend**:
    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

2.  **Run the backend** (serves frontend from same port):
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

3.  **Access the application**:
    Open [http://localhost:8000](http://localhost:8000)
    - The frontend will be served from the root path
    - API will be accessible at `/api/v1/*`
    - API documentation at `/docs`

## Docker Setup (Easiest Way)

The Docker setup automatically builds both frontend and backend into a single container.

### Production Mode (Single Container)
```bash
# Build and run everything
docker-compose up --build
```

Access at: [http://localhost:8000](http://localhost:8000)

### Development Mode (Separate Containers with Hot-Reload)
```bash
# Run with hot-reload for development
docker-compose -f docker-compose.dev.yml up --build
```

- Frontend: [http://localhost:3000](http://localhost:3000) (hot-reload enabled)
- Backend: [http://localhost:8000](http://localhost:8000)

**See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed Docker instructions.**

## Project Structure

### Backend
- `app/core`: Configuration, security, database.
- `app/models`: SQLAlchemy database models.
- `app/schemas`: Pydantic schemas for validation.
- `app/services`: Business logic layer.
- `app/api`: API routers and endpoints.

### Frontend
- `frontend/src/api`: API service layer
- `frontend/src/components`: Reusable components
- `frontend/src/pages`: Page components
- `frontend/src/store`: Zustand stores
- `frontend/src/types`: TypeScript types

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login

### Organizations
- `POST /api/v1/organizations/` - Create organization
- `GET /api/v1/organizations/` - List user's organizations
- `POST /api/v1/organizations/{org_id}/switch` - Switch organization
- `POST /api/v1/organizations/{org_id}/invite` - Generate invite token
- `POST /api/v1/organizations/join` - Join organization

### Projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/` - List projects
- `GET /api/v1/projects/{project_id}` - Get project
- `PUT /api/v1/projects/{project_id}` - Update project
- `POST /api/v1/projects/{project_id}/export` - Export project

### Notes
- `POST /api/v1/notes/` - Create note
- `GET /api/v1/notes/` - List notes
- `GET /api/v1/notes/{note_id}` - Get note
- `PUT /api/v1/notes/{note_id}` - Update note
- `POST /api/v1/notes/{note_id}/share` - Generate share link
- `DELETE /api/v1/notes/{note_id}/share` - Revoke share link
- `GET /api/v1/notes/shared/{share_token}` - View shared note (public)

### API Keys
- `POST /api/v1/api-keys/` - Create API key
- `GET /api/v1/api-keys/` - List API keys
- `DELETE /api/v1/api-keys/{key_id}` - Revoke API key

### Jobs
- `GET /api/v1/jobs/{job_id}` - Get job status

## Testing

Run tests with:
```bash
pytest
```

## Environment Variables

Create a `.env` file in the root directory:

```env
PROJECT_NAME=TeamLedger
DATABASE_URL=sqlite+aiosqlite:///./teamledger.db
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:8000
```

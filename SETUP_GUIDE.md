# TeamLedger Setup Guide

Complete guide to set up and run TeamLedger with the React frontend.

## Prerequisites

- Python 3.12 or higher
- Node.js 18 or higher
- npm or yarn

## Option 1: Development Setup (Recommended for Development)

This runs the frontend and backend on separate ports with hot-reload enabled.

### Step 1: Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at:
- API: http://localhost:8000/api/v1
- API Docs: http://localhost:8000/docs

### Step 2: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at:
- App: http://localhost:3000

The Vite dev server will proxy API requests to the backend at port 8000.

## Option 2: Production Setup (Same Port)

This builds the frontend and serves it from the backend on the same port.

### Step 1: Build Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

This creates a `frontend/dist` directory with the built static files.

### Step 2: Run Backend

```bash
# Install Python dependencies (if not done already)
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The entire application will be available at:
- App: http://localhost:8000
- API: http://localhost:8000/api/v1
- API Docs: http://localhost:8000/docs

## First Time Usage

1. **Register a new account**:
   - Go to http://localhost:3000 (dev) or http://localhost:8000 (prod)
   - Click "Register"
   - Fill in your details and create an account

2. **Login**:
   - Use your credentials to log in

3. **Create an Organization**:
   - Go to "Organizations"
   - Click "Create Organization"
   - Enter a name for your organization

4. **Create a Project**:
   - Go to "Projects"
   - Click "Create Project"
   - Fill in project details

5. **Create Notes**:
   - Click on a project
   - Click "Create Note"
   - Add notes to your project

6. **Generate API Keys** (Optional):
   - Go to "API Keys"
   - Click "Create API Key"
   - Select scopes and save the key securely

## Environment Configuration

Create a `.env` file in the root directory to customize settings:

```env
# Project
PROJECT_NAME=TeamLedger

# Database
DATABASE_URL=sqlite+aiosqlite:///./teamledger.db

# Security
SECRET_KEY=your-secure-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Frontend
FRONTEND_URL=http://localhost:8000

# CORS (for development)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
docker-compose up --build
```

Access the application at http://localhost:8000

## Troubleshooting

### Frontend can't connect to backend

**Development Mode:**
- Ensure backend is running on port 8000
- Check `frontend/vite.config.ts` proxy configuration

**Production Mode:**
- Ensure frontend is built: `cd frontend && npm run build`
- Check that `frontend/dist` directory exists

### CORS Errors

- Check that CORS middleware is enabled in `app/main.py`
- Verify `BACKEND_CORS_ORIGINS` in settings includes your frontend URL

### Database Errors

- Delete `teamledger.db` file and restart the backend to reset the database
- Check that all migrations are applied

### Port Already in Use

- Change the port in the startup command:
  ```bash
  uvicorn app.main:app --port 8001
  ```
- Update `FRONTEND_URL` in settings accordingly

## Features Overview

### Authentication
- Register and login with email/password
- JWT-based authentication
- Secure session management

### Organizations
- Create multiple organizations
- Invite team members via tokens
- Switch between organizations

### Projects
- Create and manage projects
- Update project status
- Export project data

### Notes
- Create, edit, and delete notes
- Version control for notes
- Share notes publicly via generated links
- Revoke share links

### API Keys
- Generate API keys for programmatic access
- Scope-based permissions (read, write, admin)
- Revoke keys when needed

### Background Jobs
- Track export job status
- Async processing of large operations

## Next Steps

- Explore the API documentation at `/docs`
- Check out the codebase structure in the README
- Start building your projects and notes!

## Support

For issues or questions, please create an issue in the GitHub repository.

# TeamLedger Docker Guide

Complete guide for running TeamLedger with Docker.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose

## Option 1: Production Mode (Recommended)

This builds both frontend and backend into a single container and serves everything from port 8000.

### Quick Start

```bash
docker-compose up --build
```

The application will be available at:
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### What Happens:

1. **Stage 1**: Builds the React frontend using Node.js
2. **Stage 2**: Creates Python backend container and copies the built frontend
3. **Result**: Single container serving both frontend and backend on port 8000

### Stop the Application

```bash
docker-compose down
```

### Rebuild After Changes

```bash
docker-compose up --build
```

## Option 2: Development Mode

This runs frontend and backend in separate containers with hot-reload enabled.

### Start Development Containers

```bash
docker-compose -f docker-compose.dev.yml up --build
```

The application will be available at:
- **Frontend**: http://localhost:3000 (with hot-reload)
- **Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### What Happens:

1. **Backend Container**: Runs Python with volume mount for hot-reload
2. **Frontend Container**: Runs Vite dev server with hot-reload
3. **Result**: Separate containers for easier development

### Stop Development Containers

```bash
docker-compose -f docker-compose.dev.yml down
```

## Data Persistence

Both configurations use Docker volumes to persist data:

```yaml
volumes:
  - ./data:/app/data        # Database storage
  - ./exports:/app/exports  # Export files
```

These directories will be created on your host machine and data will persist even after containers are stopped.

## Environment Variables

You can customize the application by editing the `docker-compose.yml` file or creating a `.env` file:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/teamledger.db
SECRET_KEY=your-secure-secret-key-here
FRONTEND_URL=http://localhost:8000
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Common Docker Commands

### View Running Containers
```bash
docker ps
```

### View Container Logs
```bash
# Production
docker-compose logs -f

# Development
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker logs teamledger -f
```

### Restart Containers
```bash
# Production
docker-compose restart

# Development
docker-compose -f docker-compose.dev.yml restart
```

### Remove All Containers and Volumes
```bash
# Production
docker-compose down -v

# Development
docker-compose -f docker-compose.dev.yml down -v
```

### Execute Commands Inside Container
```bash
# Production
docker exec -it teamledger bash

# Check Python version
docker exec -it teamledger python --version

# Run database migrations
docker exec -it teamledger python -m alembic upgrade head
```

### Rebuild Without Cache
```bash
docker-compose build --no-cache
docker-compose up
```

## Dockerfile Structure

### Production Dockerfile (Multi-stage)

```dockerfile
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder
# ... builds React app

# Stage 2: Python Backend + Built Frontend
FROM python:3.12-slim
# ... copies frontend/dist from stage 1
```

**Benefits:**
- Smaller final image (no Node.js in production)
- Single container to deploy
- Optimized for production

### Development Dockerfile

Simpler Dockerfile focused on backend only:
- Volume mounts for hot-reload
- Separate frontend container with Vite
- Faster development cycle

## Health Check

The production docker-compose includes a health check:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Check container health:
```bash
docker inspect --format='{{.State.Health.Status}}' teamledger
```

## Troubleshooting

### Port Already in Use

If port 8000 or 3000 is already in use, change it in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Host:Container
```

### Container Won't Start

Check logs:
```bash
docker-compose logs
```

### Database Issues

Remove the volume and restart:
```bash
docker-compose down -v
rm -rf ./data
docker-compose up --build
```

### Frontend Build Fails

Ensure you have the frontend directory with all files:
```bash
ls frontend/
# Should show: src/, package.json, vite.config.ts, etc.
```

### Memory Issues

Increase Docker Desktop memory:
- Docker Desktop → Settings → Resources → Memory
- Recommended: At least 4GB

## Production Deployment

For production deployment to cloud platforms:

### 1. Build the Image

```bash
docker build -t teamledger:latest .
```

### 2. Tag for Registry

```bash
docker tag teamledger:latest your-registry/teamledger:latest
```

### 3. Push to Registry

```bash
docker push your-registry/teamledger:latest
```

### 4. Deploy to Server

```bash
docker pull your-registry/teamledger:latest
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-production-secret \
  -e DATABASE_URL=your-db-url \
  -v /path/to/data:/app/data \
  your-registry/teamledger:latest
```

## Docker Compose Commands Reference

| Command | Description |
|---------|-------------|
| `docker-compose up` | Start containers |
| `docker-compose up -d` | Start in detached mode |
| `docker-compose up --build` | Rebuild and start |
| `docker-compose down` | Stop and remove containers |
| `docker-compose down -v` | Stop and remove volumes |
| `docker-compose logs -f` | Follow logs |
| `docker-compose ps` | List containers |
| `docker-compose restart` | Restart containers |
| `docker-compose exec web bash` | Enter container shell |

## Best Practices

1. **Change SECRET_KEY** in production
2. **Use environment files** for sensitive data
3. **Regular backups** of `./data` directory
4. **Monitor logs** for errors
5. **Update images** regularly for security patches
6. **Use specific versions** instead of `latest` in production

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify containers are running: `docker ps`
3. Check health: `docker inspect teamledger`
4. Review this guide for common issues

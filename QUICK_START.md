# TeamLedger - Quick Start Guide

Choose your preferred method to run TeamLedger:

## 🐳 Docker (Recommended - Easiest)

### Production Mode
```bash
docker-compose up --build
```
✅ Everything runs on http://localhost:8000

### Development Mode
```bash
docker-compose -f docker-compose.dev.yml up --build
```
✅ Frontend: http://localhost:3000 (with hot-reload)
✅ Backend: http://localhost:8000

📖 See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for more details

---

## 💻 Manual Setup

### Windows Users (Batch Scripts)

1. **Install Dependencies**
   ```cmd
   install-dependencies.bat
   ```

2. **Start Development Mode**
   ```cmd
   start-dev.bat
   ```
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

3. **OR Build and Run Production**
   ```cmd
   build-and-run.bat
   ```
   - Everything: http://localhost:8000

### Linux/Mac Users

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && cd ..
   ```

2. **Development Mode**
   ```bash
   # Terminal 1 - Backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

3. **Production Mode**
   ```bash
   # Build frontend
   cd frontend && npm run build && cd ..

   # Run backend (serves frontend)
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

📖 See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions

---

## 🎯 First Steps

1. **Open the application** in your browser
2. **Register** a new account
3. **Create** an organization
4. **Create** a project
5. **Add** notes to your project
6. **Generate** API keys (optional)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main project documentation |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed manual setup |
| [DOCKER_GUIDE.md](DOCKER_GUIDE.md) | Complete Docker guide |
| [frontend/README.md](frontend/README.md) | Frontend-specific docs |

---

## 🔗 URLs

### Development Mode
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- API Docs: http://localhost:8000/docs

### Production Mode
- Application: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🛠️ Troubleshooting

### Port Already in Use
- Change ports in `docker-compose.yml` or startup commands

### Database Issues
- Delete `teamledger.db` file and restart
- Docker: `docker-compose down -v` and restart

### Frontend Not Loading
- Check `frontend/dist` folder exists (production)
- Ensure backend is running (development)

### CORS Errors
- Verify backend is running on port 8000
- Check CORS middleware in `app/main.py`

---

## 📦 What's Included

✅ Complete React + TypeScript frontend
✅ FastAPI Python backend
✅ User authentication (JWT)
✅ Multi-tenant organizations
✅ Projects and notes management
✅ Note sharing (public links)
✅ API key management
✅ Background jobs
✅ Docker support
✅ Production-ready

---

## 🚀 Quick Commands Cheat Sheet

```bash
# Docker Production
docker-compose up --build

# Docker Development
docker-compose -f docker-compose.dev.yml up --build

# Manual - Backend
uvicorn app.main:app --reload

# Manual - Frontend Dev
cd frontend && npm run dev

# Manual - Frontend Build
cd frontend && npm run build

# View Logs
docker-compose logs -f

# Stop Everything
docker-compose down
```

---

## 💡 Tips

- Use **Docker** for the quickest start
- Use **Development Mode** when coding
- Use **Production Mode** for deployment
- Always **change SECRET_KEY** in production
- **Backup** the `./data` directory regularly

---

Happy coding! 🎉

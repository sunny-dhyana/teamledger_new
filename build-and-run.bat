@echo off
echo ===================================
echo Building and Running TeamLedger (Production Mode)
echo ===================================
echo.

echo Building Frontend...
cd frontend
call npm install
call npm run build
cd ..

echo.
echo Starting Backend Server (with frontend)...
start "TeamLedger" cmd /k "uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo.
echo ===================================
echo TeamLedger is starting...
echo ===================================
echo Access the application at:
echo http://localhost:8000
echo.
echo API Documentation:
echo http://localhost:8000/docs
echo ===================================
echo.
echo Press any key to close this window (server will keep running)
pause > nul

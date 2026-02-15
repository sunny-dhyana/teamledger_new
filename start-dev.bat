@echo off
echo ===================================
echo Starting TeamLedger (Development Mode)
echo ===================================
echo.

echo Starting Backend Server...
start "TeamLedger Backend" cmd /k "uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo Starting Frontend Dev Server...
start "TeamLedger Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================
echo TeamLedger is starting...
echo ===================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ===================================
echo.
echo Press any key to close this window (servers will keep running)
pause > nul

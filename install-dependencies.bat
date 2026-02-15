@echo off
echo ===================================
echo Installing TeamLedger Dependencies
echo ===================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installing Frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo ===================================
echo Installation Complete!
echo ===================================
echo.
echo To start in development mode:
echo   Run: start-dev.bat
echo.
echo To build and run in production mode:
echo   Run: build-and-run.bat
echo.
echo ===================================
pause

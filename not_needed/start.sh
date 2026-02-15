#!/bin/bash

# TeamLedger - Development Startup Script
# This script starts both the backend and frontend servers

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   TeamLedger Development Server${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if virtual environment exists
if [ ! -d "pythonvenv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv pythonvenv
fi

# Activate virtual environment
echo -e "${GREEN}Activating Python virtual environment...${NC}"
source pythonvenv/bin/activate

# Install/update backend dependencies
echo -e "${GREEN}Installing backend dependencies...${NC}"
pip install -q -r requirements.txt

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${GREEN}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Create data directory if it doesn't exist
mkdir -p data

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Starting servers...${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend server in background
echo -e "${GREEN}[1/2] Starting Backend (FastAPI)...${NC}"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Backend running on http://localhost:8000${NC}"
    echo -e "  API Docs: http://localhost:8000/docs"
else
    echo -e "${RED}✗ Backend failed to start. Check backend.log${NC}"
    exit 1
fi

# Start frontend server in background
echo -e "\n${GREEN}[2/2] Starting Frontend (Vite)...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✓ Frontend running on http://localhost:5173${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check frontend.log${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}   All servers running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\n${YELLOW}Access the application:${NC}"
echo -e "  Frontend:  ${GREEN}http://localhost:5173${NC}"
echo -e "  Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Logs:${NC}"
echo -e "  Backend:   tail -f backend.log"
echo -e "  Frontend:  tail -f frontend.log"
echo -e "\n${RED}Press Ctrl+C to stop all servers${NC}\n"

# Wait for user to stop
wait

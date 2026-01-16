@echo off
echo ===================================================
echo     MULTIMODAL ATTENDANCE AGENT LAUNCHER
echo ===================================================
echo.
echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && call venv\Scripts\activate 2>nul || echo No venv && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo    -> Backend will run at: http://localhost:8000
echo.

echo [2/2] Starting Frontend Dashboard...
start "Frontend Dashboard" cmd /k "cd frontend && npm run dev"
echo    -> Frontend will run at: http://localhost:5173
echo.
echo ===================================================
echo  startup complete! Please check the 2 new windows.
echo  Access the dashboard here: http://localhost:5173
echo ===================================================
pause

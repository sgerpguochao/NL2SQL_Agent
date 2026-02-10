@echo off
chcp 65001 >nul
set ROOT=%~dp0
cd /d "%ROOT%"

echo [NL2SQL] Starting backend (port 8118)...
start "NL2SQL-Backend" cmd /k "cd /d "%ROOT%backend" && python -m uvicorn app.main:app --reload --port 8118"

timeout /t 2 /nobreak >nul

echo [NL2SQL] Starting frontend (port 5173, host 0.0.0.0)...
start "NL2SQL-Frontend" cmd /k "cd /d "%ROOT%frontend" && npx vite --host 0.0.0.0"

echo.
echo [NL2SQL] Backend:  http://127.0.0.1:8118
echo [NL2SQL] Frontend: http://0.0.0.0:5173  (also http://127.0.0.1:5173)
echo [NL2SQL] Close the opened windows or run stop.bat to stop.
pause

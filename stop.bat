@echo off
chcp 65001 >nul
echo [NL2SQL] Stopping backend (port 8118) and frontend (port 5173)...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8118 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)

echo [NL2SQL] Done.
pause

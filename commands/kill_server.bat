@echo off
title Kill Apex Coach Server
cd /d "%~dp0.."

echo ========================================================
echo   TERMINATING APEX FITNESS COACH SERVER (PORT 8080)
echo ========================================================

set FOUND=0

:: Check PID file first if present
if exist "bridge\.server.pid" (
    set /p SERVER_PID=<"bridge\.server.pid"
    if defined SERVER_PID (
        echo [1] Found PID %SERVER_PID% in bridge\.server.pid. Terminating...
        taskkill /F /PID %SERVER_PID% >nul 2>&1
        if %errorlevel% equ 0 (
            echo     Process PID %SERVER_PID% killed successfully.
            set FOUND=1
        )
        del "bridge\.server.pid" >nul 2>&1
    )
)

:: Find and kill any process listening on port 8080
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo [2] Terminating process on port 8080 - PID %%a
    taskkill /F /PID %%a >nul 2>&1
    if %errorlevel% equ 0 (
        echo     PID %%a terminated successfully.
        set FOUND=1
    )
)

echo.
if "%FOUND%"=="1" (
    echo ========================================================
    echo   SERVER TERMINATION COMPLETE: Port 8080 is now free.
    echo ========================================================
) else (
    echo [INFO] No active server was found running on port 8080.
)

echo.
ping 127.0.0.1 -n 2 >nul

@echo off
title Kill Apex Coach Server and Tunnel
cd /d "%~dp0.."

echo ========================================================
echo   TERMINATING APEX FITNESS COACH SERVER AND TUNNEL
echo ========================================================

set FOUND=0

:: 1. Check server PID file
if exist "bridge\.server.pid" (
    set /p SERVER_PID=<"bridge\.server.pid"
    if defined SERVER_PID (
        echo [1] Terminating Server PID %SERVER_PID%...
        taskkill /F /PID %SERVER_PID% >nul 2>&1
        if %errorlevel% equ 0 set FOUND=1
        del "bridge\.server.pid" >nul 2>&1
    )
)

:: 2. Check tunnel PID file
if exist "bridge\.tunnel.pid" (
    set /p TUNNEL_PID=<"bridge\.tunnel.pid"
    if defined TUNNEL_PID (
        echo [2] Terminating Tunnel PID %TUNNEL_PID%...
        taskkill /F /PID %TUNNEL_PID% >nul 2>&1
        if %errorlevel% equ 0 set FOUND=1
        del "bridge\.tunnel.pid" >nul 2>&1
    )
)

:: 3. Terminate any cloudflared.exe instances
taskkill /F /IM cloudflared.exe >nul 2>&1
if %errorlevel% equ 0 set FOUND=1

:: 4. Clean up any port 8080 listeners
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo [3] Terminating process on port 8080 - PID %%a
    taskkill /F /PID %%a >nul 2>&1
    if %errorlevel% equ 0 set FOUND=1
)

:: Clean runtime tunnel url
if exist "bridge\.tunnel_url.txt" del "bridge\.tunnel_url.txt" >nul 2>&1

echo.
if "%FOUND%"=="1" (
    echo ========================================================
    echo   TERMINATION COMPLETE: Server and Tunnel Stopped.
    echo ========================================================
) else (
    echo [INFO] No active server or tunnel processes were running.
)

echo.
ping 127.0.0.1 -n 2 >nul

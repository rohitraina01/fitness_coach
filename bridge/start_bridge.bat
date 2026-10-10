@echo off
title Apex Fitness Mobile Bridge
echo ========================================================
echo   STARTING APEX FITNESS COACH MOBILE BRIDGE...
echo ========================================================
cd /d "%~dp0\.."

:: Check local IP
echo Your Local Network IP Addresses:
ipconfig | findstr /i "IPv4"
echo.
echo ========================================================
echo Access on this PC:    http://localhost:8080
echo Access on your Phone: http://^<YOUR-IP^>:8080 (on same Wi-Fi)
echo Or access via Cloudflare Tunnel / Tailscale from anywhere!
echo ========================================================
echo.

python "%~dp0server.py"
pause

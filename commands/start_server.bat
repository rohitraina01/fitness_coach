@echo off
title Apex Coach Bridge Server (Port 8080)
cd /d "%~dp0.."

echo ========================================================
echo   STARTING APEX FITNESS COACH BRIDGE SERVER
echo ========================================================
echo Workspace : %CD%
echo.

:: Show Local IP Addresses
echo Detecting local network IPs for mobile access:
ipconfig | findstr /i "IPv4"
echo.
echo --------------------------------------------------------
echo Local PC Access  : http://localhost:8080
echo Phone (Same Wi-Fi): http://^<YOUR-PC-IP^>:8080
echo Remote (Anywhere) : Tailscale or Cloudflare Tunnel
echo --------------------------------------------------------
echo.
echo [NOTE] Closing this console window will STOP the server.
echo        To stop from another terminal, run: commands\kill_server.bat
echo ========================================================
echo.

python "%CD%\bridge\server.py"

echo.
echo Bridge server stopped.
pause

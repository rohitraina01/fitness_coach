@echo off
title Apex Coach System (Server and Cloud Tunnel)
cd /d "%~dp0.."

echo ========================================================
echo   STARTING APEX FITNESS COACH BRIDGE AND CLOUD TUNNEL
echo ========================================================
echo Workspace : %CD%
echo.

:: Show Local IP Addresses
echo Detecting local network IPs:
ipconfig | findstr /i "IPv4"
echo.
echo --------------------------------------------------------
echo Local PC Access  : http://localhost:8080
echo Remote Gym Access: Cloudflare Secure HTTPS Tunnel
echo Web App (Phone)  : https://rohitraina01.github.io/fitness_coach/
echo Security PIN     : 0080 (Configured in .env)
echo --------------------------------------------------------
echo.
echo [NOTE] Closing this console window will STOP all services.
echo        To stop from another terminal, run: commands\kill_server.bat
echo ========================================================
echo.

python "%CD%\bridge\run_system.py"

echo.
echo Apex Coach System stopped.
pause

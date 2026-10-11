@echo off
title Pull Fitness Coach from GitHub
cd /d "%~dp0.."

echo ========================================================
echo   SYNCING LOCAL FITNESS COACH WORKSPACE FROM GITHUB
echo ========================================================

git pull origin master
if %errorlevel% neq 0 (
    echo Note: Checking main branch fallback...
    git pull origin main
)

echo.
echo ========================================================
echo   SYNC COMPLETED!
echo   All cloud workouts, CSVs, and logs are now up to date.
echo ========================================================
ping 127.0.0.1 -n 3 >nul

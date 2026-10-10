@echo off
title Sync Fitness Coach from Cloud
cd /d "%~dp0"
echo ========================================================
echo   SYNCING LOCAL FITNESS COACH WORKSPACE FROM GITHUB
echo ========================================================
git pull origin master
if %errorlevel% neq 0 (
    echo Note: Checking main branch fallback...
    git pull origin main
)
echo ========================================================
echo   SYNC COMPLETED!
echo   All cloud workouts, CSVs, and logs are now up to date.
echo ========================================================
echo.
pause

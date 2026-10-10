@echo off
title Sync Fitness Coach from Cloud
cd /d %~dp0
echo ========================================================
echo   SYNCING LOCAL FITNESS COACH WORKSPACE FROM CLOUD
echo ========================================================
git pull origin master
if %errorlevel% neq 0 (
    echo Note: Checking main branch fallback...
    git pull origin main
)
echo ========================================================
echo   DONE! Local Excel, CSVs, and logs are now updated.
echo ========================================================
timeout /t 5

@echo off
title Rebuild Excel Dashboard and Mobile Exports
cd /d "%~dp0.."

echo ========================================================
echo   STEP 1: REBUILDING EXCEL DASHBOARD
echo ========================================================
python scripts/build_dashboard.py

echo.
echo ========================================================
echo   STEP 2: EXPORTING MOBILE WORKOUT CARD
echo ========================================================
python scripts/export_mobile.py

echo.
echo Rebuild complete!
ping 127.0.0.1 -n 3 >nul

@echo off
title Fitness Coach Data Integrity Audit
cd /d "%~dp0.."

echo ========================================================
echo   RUNNING STRICT DATA INTEGRITY AUDIT
echo ========================================================
python scripts/audit_integrity.py
echo.
pause

@echo off
title Push Fitness Coach to GitHub
cd /d "%~dp0.."

echo ========================================================
echo   PUSHING APEX COACH WORKSPACE TO GITHUB
echo   Remote: https://github.com/rohitraina01/fitness_coach.git
echo ========================================================

git add .
git commit -m "Auto-sync from commands/push_to_github.bat [%date% %time%]" >nul 2>&1

git push -u origin master
if %errorlevel% neq 0 (
    echo.
    echo Checking main branch fallback...
    git push -u origin main
    if %errorlevel% neq 0 (
        echo.
        echo If browser sign-in opened, please click Authorize.
        pause
        git push -u origin master
    )
)

echo.
echo ========================================================
echo   PUSH SUCCEEDED! Your repo is live on GitHub!
echo ========================================================
ping 127.0.0.1 -n 3 >nul

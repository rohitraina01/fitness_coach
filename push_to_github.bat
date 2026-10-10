@echo off
title Push Fitness Coach to GitHub
cd /d "%~dp0"
echo ========================================================
echo   PUSHING APEX COACH WORKSPACE TO GITHUB
echo   Remote: https://github.com/rohitraina01/fitness_coach.git
echo ========================================================
git push -u origin master
if %errorlevel% neq 0 (
    echo.
    echo If browser sign-in opened, please click Authorize.
    pause
    git push -u origin master
)
echo ========================================================
echo   PUSH SUCCEEDED! Your repo is live on GitHub!
echo ========================================================
pause

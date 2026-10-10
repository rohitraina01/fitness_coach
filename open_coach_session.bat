@echo off
title Launch Antigravity Coach Session
cd /d "%~dp0"
echo ========================================================
echo   STEP 1: SYNCING LATEST WORKOUTS FROM GITHUB CLOUD
echo ========================================================
git pull origin master

echo ========================================================
echo   STEP 2: OPENING ANTIGRAVITY AGENT CHAT SESSION
echo   Model: Gemini 3.8 Flash
echo ========================================================
agy chat -r -m agent "Review recent workouts in DATA/workouts.csv and WORKOUT_LOGS/, evaluate progressive overload under double-progression rules, update CURRENT_STATUS.md and CURRENT_NEXT_WORKOUT.md, and provide concise coaching feedback."

echo ========================================================
echo   SESSION LAUNCHED IN ANTIGRAVITY!
echo ========================================================
timeout /t 3

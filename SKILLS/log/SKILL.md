---
name: log
description: Ingests incoming workout logs from the buffer (WORKOUT_LOGS/incoming_raw_log.txt) or chat, executes the 7-stage coaching workflow, and updates mobile exports.
---

# SKILL: WORKOUT LOGGING & INGESTION (/log)

## 1. PURPOSE & INVOCATION TRIGGER
Triggered when the trainee runs `/log` or says "process my incoming log", or submits raw workout notes in chat.

## 2. INPUTS & PREREQUISITES
- Incoming log buffer: `WORKOUT_LOGS/incoming_raw_log.txt` (received from mobile web app commits) or raw text pasted directly into chat.
- Canonical catalogs: `DATA/exercise_catalog.csv` and `EXERCISE_CATALOG.md`.
- Historical baselines: `DATA/workout_sets.csv` and `COACH_MEMORY.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Sync Remote Buffer**: Check if the mobile app pushed new logs to remote `origin/master` by running `git pull origin master`.
2. **Buffer Inspection & Validation**: Read `WORKOUT_LOGS/incoming_raw_log.txt`. If text is present, extract session name, date, duration, exercises, sets, reps, load, and RIR.
3. **Double-Progression & Fatigue Analysis**: Compare each set against previous session and PR baselines under double progression rules.
4. **Execute Ingestion**:
   - Run `python scripts/ingest_workout.py --from-buffer` (or pass `--notes`).
   - Ensure buffer is reset to `(No pending unprocessed logs)`.
5. **Update State Files**:
   - Update `COACH_MEMORY.md` (recovery map, volume, progressive overload notes).
   - Update `CURRENT_STATUS.md` with latest metrics and current active day.
   - Advance and prescribe the next workout in `CURRENT_NEXT_WORKOUT.md` following the program rotation and recovery rules.
   - Record entry in `CHANGELOG.md`.
6. **Rebuild & Export**:
   - Rebuild Excel dashboard: `python scripts/build_dashboard.py`.
   - Rebuild mobile app assets: `python scripts/export_mobile.py`.
   - Verify integrity: `python scripts/audit_integrity.py`.
7. **Sync & Deploy**: Commit and push changes to `origin/master` so the mobile web app immediately updates on the trainee's phone.
8. **Deliver Feedback**: Provide strict, objective feedback to the trainee on progressive overload, technical execution, and next workout targets.

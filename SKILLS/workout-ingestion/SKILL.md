---
name: workout-ingestion
description: Ingests raw or narrative workout text, extracts exercises, sets, reps, load, and normalizes them into structured records and markdown logs.
---

# SKILL: WORKOUT INGESTION

## 1. PURPOSE & INVOCATION TRIGGER
Triggered automatically when the trainee submits a completed workout report, raw notes, gym app export, or runs `/log` / "process my incoming log".

## 2. INPUTS & PREREQUISITES
- Raw workout report text from trainee (in chat or buffered in `WORKOUT_LOGS/incoming_raw_log.txt`).
- Current date and session context (or inferred from timestamp).
- Reference catalog: `DATA/exercise_catalog.csv` and `EXERCISE_CATALOG.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Raw Preservation**: Capture the trainee's raw text verbatim. If triggered via `/log` without inline text, check `WORKOUT_LOGS/incoming_raw_log.txt`.
2. **Entity Extraction**:
   - Map each logged exercise to a canonical `exercise_id` in `DATA/exercise_catalog.csv`.
   - Parse sets: determine if each set is a Warm-up (`W`), normal Working Set (`S`), Drop Set (`D`), or Rest-Pause (`RP`).
   - Extract Load (standardize to kilograms), Reps, RIR/RPE, and rest times.
3. **Ambiguity Resolution**:
   - For dumbbell exercises, ensure weight is recorded as **load per hand**, not combined.
   - For machine variations, note machine brand/pin number if specified.
4. **ID Generation**:
   - Generate `workout_id`: `W-YYYYMMDD-01`.
   - Generate `set_id`s: `S-YYYYMMDD-01-01`, `S-YYYYMMDD-01-02`, etc.
5. **Execution of Automation**:
   - If buffer has content: execute `python scripts/ingest_workout.py --from-buffer`.
   - Or execute `python scripts/ingest_workout.py --notes "<raw_text>"` with appropriate `--type`.
   - Clear `WORKOUT_LOGS/incoming_raw_log.txt` back to `(No pending unprocessed logs)`.
   - Execute `python scripts/export_mobile.py` and commit/push to git.

## 4. OUTPUTS
- Appended row in `DATA/workouts.csv`.
- Appended rows in `DATA/workout_sets.csv`.
- New markdown log in `WORKOUT_LOGS/YYYY/YYYY-MM/YYYY-MM-DD_<type>.md`.

## 5. VALIDATION & ERROR HANDLING
- Confirm no duplicate `workout_id` exists in `DATA/workouts.csv`.
- Confirm every `exercise_id` resolves to a known entry in `DATA/exercise_catalog.csv`.
- If an exercise is unrecognized, prompt trainee or add to catalog with documented biomechanical tags before saving.

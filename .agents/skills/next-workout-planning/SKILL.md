---
name: next-workout-planning
description: Dynamically synthesizes the optimal next session prescription in real time from CSV history, recovery telemetry, and exercise science (never copying static templates).
---

# SKILL: DYNAMIC NEXT WORKOUT PLANNING

## 1. PURPOSE & INVOCATION TRIGGER
Triggered after completing workout analysis, or when the trainee requests or unlocks their upcoming gym prescription.

## 2. INPUTS & PREREQUISITES
- Live telemetry script: `python scripts/coach_brief_context.py` (reads `DATA/workouts.csv`, `DATA/workout_sets.csv`, `DATA/exercise_catalog.csv`).
- Dynamic coaching framework & approved exercise pool: `CURRENT_PROGRAM.md`.
- Continuous recovery, soreness, and outside-activity context: `COACH_MEMORY.md`.
- Physique priorities & progression rules: `GOALS.md` and `COACHING_RULES.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Run Real-Time Telemetry Brief**:
   - Execute `python scripts/coach_brief_context.py`.
   - Inspect Rule 9 status (consecutive upper sessions), days since each muscle group was trained, 14-day volume per muscle, and per-exercise last session + PR + layoff flags (`>14d`).
2. **Reason & Select Session Focus Dynamically (Zero Static Templates)**:
   - Do **not** blindly copy a static "Day 1..5" recipe. Choose the optimal focus (`Push`, `Pull`, or `Legs & Core`) based on Rule 9, muscular freshness, and recent training gaps.
   - Select movements from `CURRENT_PROGRAM.md`'s approved pool that maximize Tier-1 aesthetic priorities (`Lateral Delts`, `Lats/Upper Back`, `Arms`, `Upper Chest`) and account for layoffs (e.g., if triceps haven't been trained in 14 days, prioritize stretch-mediated `OVERHEAD_TRICEPS_EXT`).
3. **Engineer Interleaved Sequencing (Rule 10)**:
   - Never stack two exercises with the same primary muscle group consecutively.
   - Interleave non-competing movements (e.g., Lateral Delts between Chest presses; Rear Delts & Biceps between Back pulls; Leg Curl between Leg Press & Leg Extension).
4. **Compute CSV-Grounded Targets (Floor / Main / Stretch)**:
   - Base every load strictly on `DATA/workout_sets.csv` + gym equipment constraints (no 6 kg DBs, no fractional heavy cable pins, no Standing Calf Raise Machine).
   - If an exercise hasn't been performed in >14 days, include a mandatory submaximal feeler set before the top working set.
5. **Write Complete Mobile-Ready Prescription**:
   - Every exercise in `CURRENT_NEXT_WORKOUT.md` MUST include `Order Rationale`, `Working Sets`, `Target Weight`, `Gym Floor Swap Option`, `Form Cue`, and `Mind-Muscle Cue`.
   - Mobility stretches must specify hold duration (`4 total holds (2 per leg) × 30–45 sec`), never rep ranges.
6. **Export & Verify**:
   - Update `CURRENT_NEXT_WORKOUT.md` and `CURRENT_STATUS.md`.
   - Run `python scripts/export_mobile.py`.
   - Run `python scripts/audit_program.py` and `python scripts/audit_integrity.py`.

## 4. OUTPUTS
- Dynamically engineered `CURRENT_NEXT_WORKOUT.md`.
- Synchronized `OUTPUTS/mobile/`, `docs/`, and `bridge/web/` exports.
- Updated `CURRENT_STATUS.md`.

---
name: next-workout-planning
description: Generates precise next-session prescriptions, double-progression targets, exercise ordering, and phone-friendly exports based on actual recovery and history.
---

# SKILL: NEXT WORKOUT PLANNING

## 1. PURPOSE & INVOCATION TRIGGER
Triggered after completing workout analysis, or when the trainee requests their upcoming gym prescription.

## 2. INPUTS & PREREQUISITES
- Completed session metadata and performance outcomes from `DATA/workouts.csv` and `DATA/workout_sets.csv`.
- Master split defined in `CURRENT_PROGRAM.md`.
- Trainee goals in `GOALS.md` and progression criteria in `COACHING_RULES.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Determine Session Identity**: Identify the next chronological session in the split (enforcing Rule 9: max 2 consecutive upper sessions before Legs & Core).
2. **CSV Baseline Query (Mandatory Fact-Check)**:
   - Query `DATA/workout_sets.csv` for the exact latest working weights and reps of every programmed exercise. Never copy stale weights from memory or old markdown.
3. **Scientific Interleaved Sequencing (Rule 10)**:
   - Never stack two exercises for the same primary muscle back-to-back (e.g., interleave Lateral Delts between Chest presses; Rear Delts & Biceps between Back pulls; Leg Curl between Leg Press & Leg Extension).
   - Prescribe **Floor**, **Main**, and **Stretch** targets calibrated to verified gym equipment (no 6 kg DBs, no fractional heavy cable pins, no Standing Calf Raise Machine).
4. **Execution Cues, MMC & Stretch Formatting**:
   - Every exercise MUST include `Order Rationale`, `Working Sets`, `Target Weight`, `Gym Floor Swap Option`, `Form Cue`, and `Mind-Muscle Cue`.
   - Mobility stretches must use hold duration (e.g., `4 total holds (2 per leg) × 30–45 sec`), never rep ranges.
5. **Update Canonical Files & Audit**:
   - Update `CURRENT_NEXT_WORKOUT.md` and `CURRENT_STATUS.md`.
   - Run `python scripts/export_mobile.py`.
   - Run `python scripts/audit_program.py` and `python scripts/audit_integrity.py` to verify zero sequencing, load-jump, equipment, or mobile-card errors.

## 4. OUTPUTS
- Updated `CURRENT_NEXT_WORKOUT.md`.
- Updated `OUTPUTS/mobile/next_workout.txt` and `OUTPUTS/mobile/next_workout.html`.
- Updated `CURRENT_STATUS.md`.

## 5. VALIDATION & ERROR HANDLING
- Ensure target loads are realistic based on standard gym increments (e.g., +2 kg per dumbbell or +2.5 kg barbell, not arbitrary micro-increments).
- Confirm rest periods and set volumes match recoverable limits.

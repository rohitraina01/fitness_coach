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
1. **Determine Session Identity**: Identify the next chronological session in the split (e.g. following Push $\rightarrow$ Pull A; following Pull $\rightarrow$ Legs).
2. **Set Target Calculation**:
   - Query previous baseline performance for each programmed exercise.
   - Prescribe **Floor / Minimum Acceptable Target** (match previous session).
   - Prescribe **Main Target** (advance reps or increase load if rep ceiling was cleared).
   - Prescribe **Stretch Target** (peak recovery scenario).
3. **Execution Cues & RIR Bounds**: Include specific setup cues, bench angles, and stop criteria.
4. **Update Canonical Files**:
   - Update `CURRENT_NEXT_WORKOUT.md`.
   - Update `CURRENT_STATUS.md`.
   - Run `python scripts/export_mobile.py` to regenerate phone-friendly plain-text and mobile HTML exports in `OUTPUTS/mobile/`.

## 4. OUTPUTS
- Updated `CURRENT_NEXT_WORKOUT.md`.
- Updated `OUTPUTS/mobile/next_workout.txt` and `OUTPUTS/mobile/next_workout.html`.
- Updated `CURRENT_STATUS.md`.

## 5. VALIDATION & ERROR HANDLING
- Ensure target loads are realistic based on standard gym increments (e.g., +2 kg per dumbbell or +2.5 kg barbell, not arbitrary micro-increments).
- Confirm rest periods and set volumes match recoverable limits.

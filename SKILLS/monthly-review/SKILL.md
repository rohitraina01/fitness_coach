---
name: monthly-review
description: Evaluates multi-week hypertrophy trends, progressive overload trajectory, body-composition changes, and determines whether program or phase shifts are justified.
---

# SKILL: MONTHLY REVIEW

## 1. PURPOSE & INVOCATION TRIGGER
Triggered at the end of each calendar month or training mesocycle (every 4–6 weeks).

## 2. INPUTS & PREREQUISITES
- Monthly workout sets and progression logs from `DATA/workout_sets.csv` and `DATA/workouts.csv`.
- Anthropometric measurements from `BODY_METRICS/body_measurements.csv` and `DATA/body_metrics.csv`.
- Adherence logs from `DATA/adherence.csv`.
- Phase objectives in `GOALS.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Multi-Week Progression Analysis**:
   - Trace load and rep changes across key index lifts (Incline DB Press, Lat Pulldown, DB Lateral Raise, Overhead Cable Triceps Ext, Flat Bench Press).
   - Flag genuine mechanical tension improvements vs stagnant exercises.
2. **Body Composition Evaluation**:
   - Compare starting vs ending monthly 7-day rolling weight average.
   - Compare waist, chest, arm, and shoulder circumference measurements.
   - Confirm if waist is decreasing/holding while arm and shoulder circumferences expand.
3. **Mesocycle Programming Decisions**:
   - Decide what exercises to retain, rotate out, or emphasize for the upcoming 4 weeks.
   - Determine if a scheduled deload week or phase transition is warranted.
4. **Publish Report**:
   - Save report in `OUTPUTS/monthly-reviews/YYYY-MM_review.md`.
   - Update `CHANGELOG.md` with any program adjustments.

## 4. OUTPUTS
- Detailed report in `OUTPUTS/monthly-reviews/`.
- Program updates in `CURRENT_PROGRAM.md` (if changes are justified).
- Historical plan archived in `OUTPUTS/archived-plans/`.

## 5. VALIDATION & ERROR HANDLING
- Do not alter an exercise simply because of a single bad session. Require multiple weeks of stagnation before changing exercises.

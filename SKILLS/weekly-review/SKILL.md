---
name: weekly-review
description: Evaluates weekly training adherence, volume per muscle group, body-weight rolling trends, and largest system bottlenecks.
---

# SKILL: WEEKLY REVIEW

## 1. PURPOSE & INVOCATION TRIGGER
Triggered at the end of each training week (Sunday/Monday) or upon trainee request for weekly progress assessment.

## 2. INPUTS & PREREQUISITES
- Completed sessions for the ISO week from `DATA/workouts.csv` and `DATA/workout_sets.csv`.
- Weigh-in entries from `DATA/body_metrics.csv` and `BODY_METRICS/weigh_ins.csv`.
- Nutrition logs from `DATA/nutrition.csv`.
- Targets from `GOALS.md` and `CURRENT_PROGRAM.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Attendance & Consistency Audit**:
   - Compare planned sessions (5) against completed sessions.
   - Calculate adherence percentage (`completed / planned * 100`).
2. **Muscle Volume Aggregation**:
   - Aggregate hard working sets completed per muscle group.
   - Contrast against weekly target volume thresholds in `GOALS.md`.
   - Identify neglected areas (e.g., zero leg sets, missed pulling volume).
3. **Body Weight Rolling Delta**:
   - Calculate 7-day average scale weight for Week $N$ vs. Week $N-1$.
   - Evaluate against target rate (-0.3 kg/week).
4. **Identify Primary Bottleneck**:
   - Is performance bottlenecked by attendance, calorie under/over-consumption, poor sleep, or excessive volume?
5. **Generate Weekly Report**:
   - Write report into `OUTPUTS/weekly-reviews/YYYY-Www_review.md`.
   - Append summary row to `DATA/adherence.csv`.
   - Refresh Excel dashboard via `python scripts/build_dashboard.py`.

## 4. OUTPUTS
- Markdown report in `OUTPUTS/weekly-reviews/`.
- Updated `DATA/adherence.csv`.
- Refreshed `DASHBOARD/fitness_dashboard.xlsx`.

## 5. VALIDATION & ERROR HANDLING
- Do not draw firm conclusions if fewer than 3 weigh-ins or 2 workouts were logged. Explicitly flag data sparsity.

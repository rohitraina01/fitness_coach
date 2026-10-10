# SYSTEM CHANGELOG & VERSION HISTORY

---

### [2026-10-11 - Update 1.1] - Full Historical Workout Recovery & App Data Integration
- **Full Historical Sets Ingestion**:
  - Ingested 125 exact sets across all 7 historical workouts (2026-09-21 through 2026-10-10) with exact loads, reps, PR flags, drop set parent-child linkages, and verified durations.
  - Slashed all `INCOMPLETE_HISTORICAL` tags to `COMPLETED` (with 2026-10-01 marked `PARTIAL` for the 4 confirmed exercises).
- **Nutrition & Weight App Ingestion**:
  - Ingested 30-day empirical trends from trainee's app screenshots:
    - Latest scale weight: 71.5 kg (today, 2026-10-11); 30-day average: 72.59 kg; range: 71.5 to 73.2 kg.
    - 30-day average calories: 1,731.03 kcal/day; latest day: 1,352 kcal.
    - 30-day average protein: 108.1 g/day; lowest: 70 g; highest: 149 g.
- **Relational Databases & Dashboard**:
  - Synchronized `DATA/workouts.csv`, `DATA/workout_sets.csv`, `DATA/body_metrics.csv`, `DATA/nutrition.csv`, and regenerated `DASHBOARD/fitness_dashboard.xlsx`.
- **Validation**:
  - Verified 100% pass across all 14 unit tests and the data integrity audit script.
- **Git Commit**:
  - Committed version 1.1 into the local repository.

---

### [2026-10-11 - Initial] - System Initialization
- Created core architecture, master coach prompt, profile, goals, coaching rules, nutrition rules, data dictionary, test suites, automation scripts, and mobile exports.

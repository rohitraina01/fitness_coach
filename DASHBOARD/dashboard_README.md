# FITNESS DASHBOARD DOCUMENTATION (`fitness_dashboard.xlsx`)

The file `DASHBOARD/fitness_dashboard.xlsx` provides an integrated, automated analytics workbook generated directly from the canonical tables in `DATA/`.

---

## 1. WORKSHEETS & ARCHITECTURE

| Sheet Name | Type | Contents & Purpose |
| :--- | :--- | :--- |
| **`Executive_Dashboard`** | Executive Summary | KPI cards (Scale weight, Deficit, Protein, Adherence, Next session), goal priority table, historical session index, and coaching alerts. |
| **`Workouts`** | Relational Table | Structured table `Table_Workouts`. Synchronized with `DATA/workouts.csv`. |
| **`Workout_Sets`** | Relational Table | Structured table `Table_WorkoutSets`. Synchronized with `DATA/workout_sets.csv`. |
| **`Exercise_Catalog`** | Relational Table | Structured table `Table_ExerciseCatalog`. Synchronized with `DATA/exercise_catalog.csv`. |
| **`Body_Composition`** | Relational Table + Chart | Structured table `Table_BodyMetrics`. Fasted morning weight, 7-day rolling average, tape measurements, and **Body Weight Trend Line Chart**. |
| **`Nutrition_Activity`** | Relational Table | Structured table `Table_Nutrition`. Daily calories, macros, step counts, fluid intake, and adherence tags. |
| **`Volume_Attribution`** | Relational Table + Chart | Structured table `Table_VolumeAttribution`. Weekly target sets vs. actual sets logged by muscle group, with a **Hypertrophy Volume Bar Chart**. |
| **`Weekly_Adherence`** | Relational Table + Chart | Structured table `Table_Adherence`. Weekly planned vs. completed sessions and an **Adherence Bar Chart**. |

---

## 2. DYNAMIC TABLE & EXPANSION CAPABILITIES
- **Structured Excel Tables**: Every dataset is wrapped in an official Excel Table (`TableStyleMedium9`). When new rows are appended or refreshed via `python scripts/build_dashboard.py`, table bounds expand automatically.
- **Native Excel Charts**:
  1. *Body Weight Trend Chart*: Updates dynamically as rows are added to `Table_BodyMetrics`.
  2. *Weekly Hypertrophy Working Sets Chart*: Displays target vs actual working sets across all 12 muscle groups.
  3. *Training Adherence Chart*: Highlights week-over-week consistency and attendance gaps.

---

## 3. HOW TO REFRESH THE DASHBOARD
Whenever a new workout is ingested or a metric updated, run:
```bash
python scripts/build_dashboard.py
```
This rebuilds the workbook atomically while preserving all styles, table formatting, and charts.

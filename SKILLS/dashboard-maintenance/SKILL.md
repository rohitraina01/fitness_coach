---
name: dashboard-maintenance
description: Rebuilds, updates, and validates the Excel analytics workbook (fitness_dashboard.xlsx) using openpyxl, ensuring formulas, tables, and charts remain intact.
---

# SKILL: DASHBOARD MAINTENANCE

## 1. PURPOSE & INVOCATION TRIGGER
Triggered automatically after any workout ingestion, metric update, or weekly review. Can also be invoked manually by running `python scripts/build_dashboard.py`.

## 2. INPUTS & PREREQUISITES
- Normalized CSV files in `DATA/`: `workouts.csv`, `workout_sets.csv`, `exercise_catalog.csv`, `body_metrics.csv`, `nutrition.csv`, `adherence.csv`.
- Python runtime with `openpyxl` installed.
- Automation script `scripts/build_dashboard.py`.

## 3. STEP-BY-STEP PROCEDURE
1. **Pre-Build Validation**:
   - Verify that all CSV files exist and contain valid header rows.
   - Confirm target directory `DASHBOARD/` exists.
2. **Execute Workbook Generator**:
   - Run: `python scripts/build_dashboard.py`.
3. **Post-Build Verification**:
   - Verify `DASHBOARD/fitness_dashboard.xlsx` exists and has non-zero file size.
   - Confirm all 8 worksheets (`Executive_Dashboard`, `Workouts`, `Workout_Sets`, `Exercise_Catalog`, `Body_Composition`, `Nutrition_Activity`, `Volume_Attribution`, `Weekly_Adherence`) are present.
   - Confirm structured tables (`Table_Workouts`, etc.) and native charts (Weight Trend, Volume Attribution, Adherence) are embedded without corruption.

## 4. OUTPUTS
- Refreshed `DASHBOARD/fitness_dashboard.xlsx`.

## 5. VALIDATION & ERROR HANDLING
- If Excel file is locked because the trainee has it open in Microsoft Excel, alert trainee to save and close the workbook, then retry.

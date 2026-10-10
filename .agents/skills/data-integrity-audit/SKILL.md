---
name: data-integrity-audit
description: Audits relational consistency across CSVs, Markdown workout logs, and the Excel dashboard, detecting duplicate IDs, orphan foreign keys, and unit anomalies.
---

# SKILL: DATA INTEGRITY AUDIT

## 1. PURPOSE & INVOCATION TRIGGER
Triggered after any database modification, before finalizing reports, and periodically to guarantee data consistency.

## 2. INPUTS & PREREQUISITES
- CSV datasets in `DATA/`.
- Markdown logs in `WORKOUT_LOGS/`.
- Python script `scripts/audit_integrity.py`.

## 3. STEP-BY-STEP PROCEDURE
1. **Primary Key Uniqueness Check**:
   - Verify `workout_id`s in `workouts.csv` are unique.
   - Verify `set_id`s in `workout_sets.csv` are unique.
   - Verify `exercise_id`s in `exercise_catalog.csv` are unique.
2. **Referential Integrity Audit**:
   - Every `workout_id` in `workout_sets.csv` must exist in `workouts.csv`.
   - Every `exercise_id` in `workout_sets.csv` must exist in `exercise_catalog.csv`.
   - Any `parent_set_id` in `workout_sets.csv` must reference a valid `set_id`.
3. **Cross-Format Reconciliation**:
   - Check that every workout in `DATA/workouts.csv` has a matching markdown log in `WORKOUT_LOGS/`.
   - Verify that set counts in markdown match set counts in `workout_sets.csv`.
4. **Unit & Boundary Validation**:
   - Confirm load units are `kg` (or standard).
   - Flag negative loads, negative reps, or extreme values (>300 kg or >100 reps).
5. **Execution**:
   - Run: `python scripts/audit_integrity.py`.

## 4. OUTPUTS
- Terminal audit report and exit status (0 = Clean pass; non-zero = Discrepancies detected).

## 5. VALIDATION & ERROR HANDLING
- If discrepancies or broken links are found, halt updates, flag conflicting rows, and present exact repair steps.

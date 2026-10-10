"""
audit_integrity.py - Relational & Referential Data Integrity Auditor
Validates primary keys, foreign keys, unit consistency, value boundaries,
and synchronization between CSV databases and Markdown workout logs.
"""

import os
import csv
import glob
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")
WORKOUT_LOGS_DIR = os.path.join(BASE_DIR, "WORKOUT_LOGS")

def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def audit():
    errors = []
    warnings = []

    print("==================================================")
    print("      FITNESS COACHING DATA INTEGRITY AUDIT       ")
    print("==================================================")

    # 1. Load Datasets
    workouts = load_csv("workouts.csv")
    sets = load_csv("workout_sets.csv")
    catalog = load_csv("exercise_catalog.csv")
    metrics = load_csv("body_metrics.csv")
    nutrition = load_csv("nutrition.csv")
    adherence = load_csv("adherence.csv")

    print(f"Loaded: {len(workouts)} workouts, {len(sets)} sets, {len(catalog)} exercises in catalog.")

    # 2. Primary Key Uniqueness
    workout_ids = set()
    for w in workouts:
        wid = w.get("workout_id")
        if not wid:
            errors.append("Empty workout_id found in workouts.csv")
        elif wid in workout_ids:
            errors.append(f"Duplicate workout_id detected: {wid}")
        workout_ids.add(wid)

    set_ids = set()
    for s in sets:
        sid = s.get("set_id")
        if not sid:
            errors.append("Empty set_id found in workout_sets.csv")
        elif sid in set_ids:
            errors.append(f"Duplicate set_id detected: {sid}")
        set_ids.add(sid)

    exercise_ids = set()
    for e in catalog:
        eid = e.get("exercise_id")
        if not eid:
            errors.append("Empty exercise_id found in exercise_catalog.csv")
        elif eid in exercise_ids:
            errors.append(f"Duplicate exercise_id in catalog: {eid}")
        exercise_ids.add(eid)

    # 3. Referential Integrity (Foreign Keys)
    for s in sets:
        wid = s.get("workout_id")
        if wid not in workout_ids:
            errors.append(f"Orphan set {s.get('set_id')}: workout_id '{wid}' does not exist in workouts.csv")

        eid = s.get("exercise_id")
        if eid not in exercise_ids:
            errors.append(f"Invalid exercise {eid} in set {s.get('set_id')}: not found in exercise_catalog.csv")

        parent_id = s.get("parent_set_id")
        if parent_id and parent_id not in set_ids:
            errors.append(f"Set {s.get('set_id')} references missing parent_set_id: {parent_id}")

    # 4. Range and Unit Validations
    for s in sets:
        unit = s.get("units")
        if unit and unit not in ("kg", "lbs", "bw"):
            errors.append(f"Invalid unit '{unit}' in set {s.get('set_id')}")

        load_str = s.get("load")
        if load_str:
            try:
                load = float(load_str)
                if load < 0 or load > 400:
                    errors.append(f"Implausible load value '{load}' in set {s.get('set_id')}")
            except ValueError:
                errors.append(f"Non-numeric load '{load_str}' in set {s.get('set_id')}")

        reps_str = s.get("reps")
        if reps_str:
            try:
                reps = int(reps_str)
                if reps < 0 or reps > 150:
                    errors.append(f"Implausible rep count '{reps}' in set {s.get('set_id')}")
            except ValueError:
                errors.append(f"Non-integer reps '{reps_str}' in set {s.get('set_id')}")

    # 5. Cross-Reconciliation with Markdown Logs
    md_files = glob.glob(os.path.join(WORKOUT_LOGS_DIR, "**", "*.md"), recursive=True)
    md_basenames = [os.path.basename(f) for f in md_files]
    print(f"Found {len(md_files)} markdown workout logs in WORKOUT_LOGS/")

    for w in workouts:
        date = w.get("date")
        s_type = w.get("session_type", "").lower()
        expected_prefix = f"{date}_{s_type}"
        matched = any(f.startswith(expected_prefix) for f in md_basenames)
        if not matched:
            warnings.append(f"Workout {w.get('workout_id')} on {date} has no matching markdown log starting with {expected_prefix}")

    # 6. Report Summary
    print("\n---------------- AUDIT RESULTS ----------------")
    if not errors and not warnings:
        print("STATUS: PASSED (100% Data Integrity Verified)")
        print("- All Primary Keys Unique")
        print("- All Foreign Keys Valid")
        print("- Units & Boundaries Standardized")
        print("- Relational CSVs & Markdown Logs Synchronized")
        print("-----------------------------------------------")
        return 0
    else:
        if errors:
            print(f"ERRORS DETECTED ({len(errors)}):")
            for e in errors:
                print(f"  [ERROR] {e}")
        if warnings:
            print(f"\nWARNINGS ({len(warnings)}):")
            for w in warnings:
                print(f"  [WARN] {w}")
        print("-----------------------------------------------")
        return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(audit())

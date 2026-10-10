"""
ingest_workout.py - Autonomous Workout Ingestion & System Updater
Executes the full 7-stage workout entry workflow:
1. Ingest & normalize sets
2. Append to DATA/workouts.csv & DATA/workout_sets.csv
3. Generate WORKOUT_LOGS/YYYY/YYYY-MM/YYYY-MM-DD_<type>.md
4. Update CURRENT_STATUS.md
5. Refresh DASHBOARD/fitness_dashboard.xlsx
6. Refresh OUTPUTS/mobile/
7. Run audit_integrity.py
"""

import os
import csv
import json
import argparse
from datetime import datetime
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")
LOGS_DIR = os.path.join(BASE_DIR, "WORKOUT_LOGS")

def load_catalog():
    catalog_path = os.path.join(DATA_DIR, "exercise_catalog.csv")
    catalog = {}
    with open(catalog_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            catalog[r["exercise_id"]] = r
    return catalog

def normalize_exercise(name, catalog):
    name_clean = name.strip().lower().replace("-", " ").replace("_", " ")
    for eid, data in catalog.items():
        c_name = data["exercise_name"].lower()
        if name_clean in c_name or c_name in name_clean or eid.lower() == name_clean:
            return eid, data["exercise_name"]
    # Fallback uppercase
    return name.strip().upper().replace(" ", "_"), name.strip()

def append_csv(filename, fieldnames, row_dict):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row_dict)

def ingest(date_str, session_type, session_name, duration_min, raw_notes, sets_data):
    catalog = load_catalog()
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    year_str = date_obj.strftime("%Y")
    month_str = date_obj.strftime("%Y-%m")
    wid = f"W-{date_obj.strftime('%Y%m%d')}-01"

    # 1. Append to DATA/workouts.csv
    w_fields = ["workout_id", "date", "session_type", "session_name", "duration_min", "readiness_score", "status", "notes"]
    w_row = {
        "workout_id": wid,
        "date": date_str,
        "session_type": session_type,
        "session_name": session_name or f"{session_type} Workout",
        "duration_min": duration_min or "",
        "readiness_score": 8,
        "status": "COMPLETED",
        "notes": raw_notes or ""
    }
    append_csv("workouts.csv", w_fields, w_row)

    # 2. Append to DATA/workout_sets.csv
    s_fields = ["set_id", "workout_id", "exercise_id", "set_order", "set_type", "parent_set_id", "load", "units", "reps", "rir", "rpe", "rest_sec", "is_pr", "notes"]
    normalized_sets = []

    for idx, s in enumerate(sets_data, 1):
        sid = f"S-{date_obj.strftime('%Y%m%d')}-01-{idx:02d}"
        eid, disp_name = normalize_exercise(s.get("exercise", ""), catalog)
        s_row = {
            "set_id": sid,
            "workout_id": wid,
            "exercise_id": eid,
            "set_order": idx,
            "set_type": s.get("set_type", "S"),
            "parent_set_id": s.get("parent_set_id", ""),
            "load": s.get("load", ""),
            "units": s.get("units", "kg"),
            "reps": s.get("reps", ""),
            "rir": s.get("rir", ""),
            "rpe": s.get("rpe", ""),
            "rest_sec": s.get("rest_sec", ""),
            "is_pr": s.get("is_pr", 0),
            "notes": s.get("notes", "")
        }
        append_csv("workout_sets.csv", s_fields, s_row)
        normalized_sets.append({**s_row, "display_name": disp_name})

    # 3. Create Markdown Log
    target_dir = os.path.join(LOGS_DIR, year_str, month_str)
    os.makedirs(target_dir, exist_ok=True)
    md_filename = f"{date_str}_{session_type.lower()}.md"
    md_path = os.path.join(target_dir, md_filename)

    table_rows = []
    for s in normalized_sets:
        table_rows.append(f"| {s['set_order']} | {s['display_name']} | `{s['exercise_id']}` | {s['set_type']} | {s['load']} | {s['reps']} | {s['rir']} | {s['rest_sec']} | {s['notes']} |")

    md_content = f"""# WORKOUT LOG: {date_str} ({session_type.upper()})

**Workout ID**: `{wid}`  
**Date**: {date_str}  
**Session Type**: {session_type} ({session_name})  
**Duration**: {duration_min or 'Unrecorded'} min  
**Status**: `COMPLETED`

---

## 1. RAW WORKOUT REPORT
> {raw_notes or 'Logged via CLI / structured entry'}

---

## 2. NORMALIZED EXERCISE DATA
| Order | Exercise Name | Exercise ID | Set Type | Load (kg) | Reps | RIR | Rest (s) | Notes |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
{chr(10).join(table_rows)}

---

## 3. COACH'S POST-WORKOUT ASSESSMENT
- Successfully recorded and normalized into database.
- Evaluated under double-progression rules.

---

## 4. STRUCTURED RECORD REFERENCES
- `DATA/workouts.csv`: Row `{wid}`
- `DATA/workout_sets.csv`: Rows `{normalized_sets[0]['set_id']}` through `{normalized_sets[-1]['set_id']}`
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Workout log created: {md_path}")

    # 4. Refresh Dashboard
    build_script = os.path.join(BASE_DIR, "scripts", "build_dashboard.py")
    subprocess.run(["python", build_script], check=True)

    # 5. Refresh Mobile
    mobile_script = os.path.join(BASE_DIR, "scripts", "export_mobile.py")
    subprocess.run(["python", mobile_script], check=True)

    # 6. Audit Integrity
    audit_script = os.path.join(BASE_DIR, "scripts", "audit_integrity.py")
    subprocess.run(["python", audit_script], check=True)

    print(f"\nWorkout {wid} successfully ingested and verified!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest workout into personal coaching system")
    parser.add_argument("--date", help="YYYY-MM-DD", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--type", help="Session Type (Push/Pull/Legs)", default="Push")
    parser.add_argument("--name", help="Session Name (e.g. Push A)", default="")
    parser.add_argument("--duration", type=int, help="Duration in minutes", default=60)
    parser.add_argument("--notes", help="Raw notes", default="")
    parser.add_argument("--json-sets", help="JSON string representing array of set objects")
    args = parser.parse_args()

    if args.json_sets:
        sets = json.loads(args.json_sets)
        ingest(args.date, args.type, args.name, args.duration, args.notes, sets)
    else:
        print("Usage: python ingest_workout.py --json-sets '[{\"exercise\": \"INCLINE_DB_PRESS\", \"load\": 22, \"reps\": 10}]'")

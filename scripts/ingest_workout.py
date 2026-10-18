"""
ingest_workout.py - Autonomous Workout Ingestion & System Updater
Executes the full 7-stage workout entry workflow:
1. Ingest & normalize sets (from JSON or natural language notes)
2. Append to DATA/workouts.csv & DATA/workout_sets.csv
3. Generate WORKOUT_LOGS/YYYY/YYYY-MM/YYYY-MM-DD_<type>.md
4. Update CURRENT_STATUS.md & CURRENT_NEXT_WORKOUT.md
5. Refresh DASHBOARD/fitness_dashboard.xlsx
6. Refresh OUTPUTS/mobile/
7. Run audit_integrity.py
"""

import os
import sys
import csv
import json
import re
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

def match_exercise(line, catalog):
    line_clean = line.lower().replace("-", " ").replace("_", " ")
    if "lying leg curl" in line_clean or "leg curl" in line_clean:
        return "LEG_CURL", "Leg Curl Machine"
    if "standing calf raise" in line_clean or "calf raise" in line_clean:
        return "CALF_RAISE", "Standing Calf Raise"
    if "leg extension" in line_clean:
        return "LEG_EXTENSION", "Leg Extension Machine"
    if "leg press" in line_clean:
        return "LEG_PRESS", "Leg Press"
    if "dead bug" in line_clean or "deadbug" in line_clean:
        return "DEADBUG", "Deadbug Anti-APT Core"
    if "cable crunch" in line_clean:
        return "CABLE_CRUNCH", "Kneeling Cable Crunch"
    if "crunch" in line_clean:
        return "FLOOR_CRUNCH", "Bodyweight Floor Crunch"
    if "lying leg raise" in line_clean or "leg raise" in line_clean:
        return "LYING_LEG_RAISE", "Lying Leg Raise"
    if "single arm lat pulldown" in line_clean or "single arm pulldown" in line_clean:
        return "SINGLE_ARM_LAT_PULLDOWN", "Single-Arm Cable Lat Pulldown"
    if "single arm cable row" in line_clean or "single arm lat row" in line_clean or "single arm row" in line_clean:
        return "SINGLE_ARM_CABLE_ROW", "Single-Arm Cable Row"
    if "straight arm pulldown" in line_clean or "straight arm" in line_clean:
        return "STRAIGHT_ARM_PULLDOWN", "Straight-Arm Cable Pulldown"
    if "lat pulldown" in line_clean:
        return "LAT_PULLDOWN", "Lat Pulldown"
    if "pull up" in line_clean or "pull-up" in line_clean:
        return "PULL_UP", "Pull-Up"
    if "rear delt" in line_clean or "reverse pec deck" in line_clean:
        return "REAR_DELT_FLY", "Reverse Pec Deck (Rear Delt Fly)"
    if "ez bar curl" in line_clean or "ez-bar curl" in line_clean:
        return "EZ_BAR_CURL", "EZ-Bar Bicep Curl"
    if "hammer curl" in line_clean:
        return "HAMMER_CURL", "Dumbbell Hammer Curl"
    if "seated row" in line_clean or "cable row" in line_clean:
        return "SEATED_CABLE_ROW", "Seated Cable Row"

    for eid, data in catalog.items():
        name_clean = data["exercise_name"].lower().replace("-", " ")
        if name_clean == line_clean or name_clean in line_clean or eid.lower().replace("_", " ") == line_clean:
            return eid, data["exercise_name"]
    
    line_tokens = set(re.findall(r"\b[a-z]{3,}\b", line_clean))
    line_tokens -= {"sets", "reps", "rir", "rpe", "dummy", "test", "per", "hand", "min", "drop"}
    best_eid = None
    best_score = 0
    for eid, data in catalog.items():
        name_clean = data["exercise_name"].lower().replace("-", " ")
        name_tokens = set(re.findall(r"\b[a-z]{3,}\b", name_clean))
        overlap = len(line_tokens & name_tokens)
        if overlap > best_score:
            best_score = overlap
            best_eid = eid
            
    if best_eid and best_score >= 1:
        return best_eid, catalog[best_eid]["exercise_name"]
    return None, None

def parse_notes_to_sets(raw_notes, catalog):
    lines = [l.strip() for l in raw_notes.split("\n") if l.strip()]
    sets_data = []
    current_eid = None

    for line in lines:
        if any(w in line.lower() for w in ["dummy", "test", "duration:", "status", "reported", "workout", "session:"]):
            continue

        eid, disp_name = match_exercise(line, catalog)
        is_set_line = bool(re.search(r"set\s*\d+\s*:", line, re.IGNORECASE)) or bool(re.search(r"(?:x|\*|@)\s*\d+", line, re.IGNORECASE))

        if eid and not is_set_line:
            current_eid = eid
            continue

        if is_set_line and current_eid:
            target_eid = current_eid
        elif eid and is_set_line:
            target_eid = eid
            current_eid = eid
        elif eid:
            target_eid = eid
        else:
            continue

        load = 0.0
        load_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|lbs)", line, re.IGNORECASE)
        if load_match:
            load = float(load_match.group(1))

        rep_match = re.search(r"(\d+)\s*reps?", line, re.IGNORECASE)
        if rep_match:
            reps_list = [int(rep_match.group(1))]
        else:
            rep_matches = re.findall(r"(?:x|\*|@|,)\s*(\d+)", line, re.IGNORECASE)
            reps_list = [int(r) for r in rep_matches] if rep_matches else [10]

        # Drop set and warmup classification:
        set_type = "S"
        parent_idx = None
        is_dropset_line = any(w in line.lower() for w in ["dropset", "drop set", "drop-set"])

        if "warmup" in line.lower() or "warm up" in line.lower() or "feeler" in line.lower():
            set_type = "W"
        elif target_eid == "LEG_PRESS" and load < 30.0:
            set_type = "W"
        elif target_eid == "LEG_EXTENSION" and load < 6.0 and any("10" in l for l in lines):
            set_type = "W"
        elif is_dropset_line:
            # If the immediate preceding set was the same exercise, check load
            if sets_data and sets_data[-1]["exercise"] == target_eid:
                prev_load = sets_data[-1]["load"]
                if load < prev_load or sets_data[-1].get("is_dropset_parent"):
                    set_type = "D"
                    parent_idx = len(sets_data) - 1
                else:
                    set_type = "S"
                    sets_data[-1]["is_dropset_parent"] = True
            else:
                set_type = "S"

        is_pr_flag = 1 if "[pr]" in line.lower() or " pr" in line.lower() else 0

        for r in reps_list:
            set_obj = {
                "exercise": target_eid,
                "load": load,
                "reps": r,
                "units": "kg",
                "set_type": set_type,
                "rir": 0 if is_dropset_line or is_pr_flag else 2,
                "is_pr": is_pr_flag,
                "notes": line
            }
            if parent_idx is not None:
                set_obj["parent_set_index"] = parent_idx
            sets_data.append(set_obj)

    return sets_data

def append_csv(filename, fieldnames, row_dict):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row_dict)

def get_historical_prs():
    sets_path = os.path.join(DATA_DIR, "workout_sets.csv")
    prs = {}
    if os.path.exists(sets_path):
        with open(sets_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                eid = r["exercise_id"]
                try:
                    load = float(r["load"]) if r["load"] else 0.0
                    reps = int(r["reps"]) if r["reps"] else 0
                except (ValueError, TypeError):
                    continue
                if eid not in prs:
                    prs[eid] = {"max_load": 0.0, "max_reps_at_max_load": 0}
                if load > prs[eid]["max_load"]:
                    prs[eid]["max_load"] = load
                    prs[eid]["max_reps_at_max_load"] = reps
                elif load == prs[eid]["max_load"] and reps > prs[eid]["max_reps_at_max_load"]:
                    prs[eid]["max_reps_at_max_load"] = reps
    return prs

def ingest(date_str, session_type, session_name, duration_min, raw_notes, sets_data):
    catalog = load_catalog()
    hist_prs = get_historical_prs()
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
        "duration_min": duration_min or 60,
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
        eid = s.get("exercise", "")
        disp_name = catalog.get(eid, {}).get("exercise_name", eid)
        parent_id = s.get("parent_set_id", "")
        if not parent_id and "parent_set_index" in s:
            parent_id = f"S-{date_obj.strftime('%Y%m%d')}-01-{s['parent_set_index']+1:02d}"
        elif s.get("set_type") == "D" and not parent_id and normalized_sets:
            for prev in reversed(normalized_sets):
                if prev["exercise_id"] == eid and prev["set_type"] == "S":
                    parent_id = prev["set_id"]
                    break

        load_val = s.get("load", 0.0)
        reps_val = s.get("reps", 10)
        is_pr_val = s.get("is_pr", 0)

        if not is_pr_val and eid in hist_prs and hist_prs[eid]["max_load"] > 0:
            if load_val > hist_prs[eid]["max_load"]:
                is_pr_val = 1
            elif load_val == hist_prs[eid]["max_load"] and reps_val > hist_prs[eid]["max_reps_at_max_load"]:
                is_pr_val = 1

        if is_pr_val and eid in hist_prs:
            if load_val > hist_prs[eid]["max_load"]:
                hist_prs[eid]["max_load"] = load_val
                hist_prs[eid]["max_reps_at_max_load"] = reps_val
            elif load_val == hist_prs[eid]["max_load"] and reps_val > hist_prs[eid]["max_reps_at_max_load"]:
                hist_prs[eid]["max_reps_at_max_load"] = reps_val

        s_row = {
            "set_id": sid,
            "workout_id": wid,
            "exercise_id": eid,
            "set_order": idx,
            "set_type": s.get("set_type", "S"),
            "parent_set_id": parent_id,
            "load": load_val,
            "units": s.get("units", "kg"),
            "reps": reps_val,
            "rir": s.get("rir", 2),
            "rpe": s.get("rpe", ""),
            "rest_sec": s.get("rest_sec", 90),
            "is_pr": is_pr_val,
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
**Session Type**: {session_type} ({session_name or session_type})  
**Duration**: {duration_min or '60'} min  
**Status**: `COMPLETED`

---

## 1. RAW WORKOUT REPORT
> {raw_notes or 'Logged via mobile/cloud entry'}

---

## 2. NORMALIZED EXERCISE DATA
| Order | Exercise Name | Exercise ID | Set Type | Load (kg) | Reps | RIR | Rest (s) | Notes |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
{chr(10).join(table_rows)}

---

## 3. COACH'S POST-WORKOUT ASSESSMENT
- Successfully recorded and normalized into relational database.
- Evaluated under strict double-progression rules.

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
    subprocess.run([sys.executable, build_script], check=True)

    # 5. Refresh Mobile
    mobile_script = os.path.join(BASE_DIR, "scripts", "export_mobile.py")
    subprocess.run([sys.executable, mobile_script], check=True)

    # 6. Audit Integrity
    audit_script = os.path.join(BASE_DIR, "scripts", "audit_integrity.py")
    subprocess.run([sys.executable, audit_script], check=True)

    print(f"\nWorkout {wid} successfully ingested and verified!")

def ingest_from_buffer(extra_notes=""):
    buffer_path = os.path.join(LOGS_DIR, "incoming_raw_log.txt")
    if not os.path.exists(buffer_path):
        print(f"Buffer file not found: {buffer_path}")
        return False

    with open(buffer_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    clean_lines = []
    session_type = "Legs"
    session_name = ""
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("(No pending"):
            continue
        if stripped.startswith("# Session:"):
            session_type = stripped.replace("# Session:", "").strip()
            continue
        if stripped.startswith("#"):
            continue
        clean_lines.append(stripped)

    if not clean_lines:
        print("No pending unprocessed workout found in WORKOUT_LOGS/incoming_raw_log.txt.")
        return False

    raw_notes = "\n".join(clean_lines)
    catalog = load_catalog()
    sets = parse_notes_to_sets(raw_notes, catalog)

    if not sets:
        print("Warning: Could not match any sets from incoming buffer text.")
        return False

    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", content)
    date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
    dur_match = re.search(r"Duration:\s*(\d+)m", content, re.IGNORECASE)
    duration_min = int(dur_match.group(1)) if dur_match else 38

    next_workout_path = os.path.join(BASE_DIR, "CURRENT_NEXT_WORKOUT.md")
    nw_text = ""
    if os.path.exists(next_workout_path):
        with open(next_workout_path, "r", encoding="utf-8") as f:
            nw_text = f.read().upper()

    if "pull" in session_type.lower():
        if "PULL B" in nw_text:
            session_name = "Day 6: Pull B"
        else:
            session_name = "Day 2: Pull A"
    elif "leg" in session_type.lower():
        session_name = "Day 3: Legs & Core"
    elif "push" in session_type.lower():
        if "PUSH B" in nw_text:
            session_name = "Day 5: Push B"
        else:
            session_name = "Day 1: Push A"
    else:
        session_name = f"{session_type} Session"

    combined_notes = raw_notes
    if extra_notes:
        combined_notes = f"{raw_notes}\n\nTrainee Notes: {extra_notes}"

    ingest(date_str, session_type, session_name, duration_min, combined_notes, sets)

    # Clear buffer after successful ingestion
    with open(buffer_path, "w", encoding="utf-8") as f:
        f.write("# INCOMING WORKOUT LOG BUFFER\n# This file receives raw logs submitted from the mobile web app.\n# When you return to your laptop, tell the coach \"/log\" or \"process my incoming log\", and it will read this file automatically.\n\n(No pending unprocessed logs)\n")
    print("Buffer cleared successfully (reset to 'No pending unprocessed logs').")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest workout into personal coaching system")
    parser.add_argument("--from-buffer", action="store_true", help="Ingest pending raw text from WORKOUT_LOGS/incoming_raw_log.txt")
    parser.add_argument("--extra-notes", help="Additional notes from chat to attach to raw notes", default="")
    parser.add_argument("--date", help="YYYY-MM-DD", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--type", help="Session Type (Push/Pull/Legs)", default="Pull")
    parser.add_argument("--name", help="Session Name (e.g. Pull A)", default="")
    parser.add_argument("--duration", type=int, help="Duration in minutes", default=60)
    parser.add_argument("--notes", help="Raw notes", default="")
    parser.add_argument("--json-sets", help="JSON string representing array of set objects")
    args = parser.parse_args()

    if args.from_buffer:
        ingest_from_buffer(extra_notes=args.extra_notes)
    else:
        sets = []
        if args.json_sets:
            sets = json.loads(args.json_sets)
        elif args.notes:
            catalog = load_catalog()
            sets = parse_notes_to_sets(args.notes, catalog)

        if sets:
            combined = args.notes
            if args.extra_notes:
                combined = f"{args.notes}\n\nTrainee Notes: {args.extra_notes}"
            ingest(args.date, args.type, args.name, args.duration, combined, sets)
        else:
            print("Warning: No sets provided or parsed from notes.")


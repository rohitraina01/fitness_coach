"""
migrate_recovered_history.py - Updates all 7 historical workout records
with exact recovered sets, loads, reps, drop sets, and durations.
"""

import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")
LOGS_DIR = os.path.join(BASE_DIR, "WORKOUT_LOGS")

# Definitive recovered history
RECOVERED_WORKOUTS = [
    {
        "workout_id": "W-20260921-01",
        "date": "2026-09-21",
        "session_type": "Push",
        "session_name": "Push Workout",
        "duration_min": 85,
        "readiness_score": 8,
        "status": "COMPLETED",
        "notes": "Recovered duration 85m 19s. Set details fully recovered.",
        "sets": [
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 18, "notes": ""},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 13, "notes": ""},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 11, "notes": ""},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 10, "notes": ""},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 17.5, "reps": 12, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 8, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 6, "notes": "Per hand"},
            {"exercise": "TRICEPS_PUSHDOWN", "set_type": "S", "load": 30.0, "reps": 12, "notes": ""},
            {"exercise": "TRICEPS_PUSHDOWN", "set_type": "S", "load": 25.0, "reps": 12, "notes": ""},
            {"exercise": "TRICEPS_PUSHDOWN", "set_type": "S", "load": 25.0, "reps": 9, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 20.0, "reps": 13, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 12, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 10, "notes": ""},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 10.0, "reps": 12, "notes": "Rope extension"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 15.0, "reps": 12, "notes": "Rope extension"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 20.0, "reps": 11, "notes": "Rope extension"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 20.0, "reps": 10, "notes": "Rope extension"}
        ]
    },
    {
        "workout_id": "W-20260924-01",
        "date": "2026-09-24",
        "session_type": "Pull",
        "session_name": "Pull Day: Aesthetic Back",
        "duration_min": "",
        "readiness_score": 8,
        "status": "COMPLETED",
        "notes": "Reported duration 12m 36s marked unreliable due to delayed entry; reported volume 4,820 kg, 19 sets.",
        "sets": [
            {"exercise": "PULL_UP", "set_type": "S", "load": 0.0, "reps": 3, "units": "bw", "notes": "Body weight"},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 50.0, "reps": 8, "notes": ""},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 50.0, "reps": 6, "notes": ""},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 45.0, "reps": 7, "notes": ""},
            {"exercise": "SEATED_CABLE_ROW", "set_type": "S", "load": 60.0, "reps": 10, "notes": ""},
            {"exercise": "SEATED_CABLE_ROW", "set_type": "S", "load": 60.0, "reps": 10, "notes": ""},
            {"exercise": "SEATED_CABLE_ROW", "set_type": "S", "load": 60.0, "reps": 10, "notes": ""},
            {"exercise": "STRAIGHT_ARM_PULLDOWN", "set_type": "S", "load": 20.0, "reps": 8, "notes": ""},
            {"exercise": "STRAIGHT_ARM_PULLDOWN", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "STRAIGHT_ARM_PULLDOWN", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "REAR_DELT_FLY", "set_type": "S", "load": 15.0, "reps": 15, "notes": ""},
            {"exercise": "REAR_DELT_FLY", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "REAR_DELT_FLY", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "CABLE_CURL", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "CABLE_CURL", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "CABLE_CURL", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "HAMMER_CURL", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Per hand"},
            {"exercise": "HAMMER_CURL", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Per hand"},
            {"exercise": "HAMMER_CURL", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Per hand"}
        ]
    },
    {
        "workout_id": "W-20260925-01",
        "date": "2026-09-25",
        "session_type": "Pull",
        "session_name": "Pull Day",
        "duration_min": "",
        "readiness_score": 8,
        "status": "COMPLETED",
        "notes": "Reported 7 exercises, 21 sets. Set details fully recovered.",
        "sets": [
            {"exercise": "PULL_UP", "set_type": "S", "load": 0.0, "reps": 3, "units": "bw", "notes": "Body weight"},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 50.0, "reps": 8, "notes": ""},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 50.0, "reps": 8, "notes": ""},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 50.0, "reps": 8, "notes": ""},
            {"exercise": "SEATED_CABLE_ROW", "set_type": "S", "load": 60.0, "reps": 10, "notes": ""},
            {"exercise": "SEATED_CABLE_ROW", "set_type": "S", "load": 60.0, "reps": 10, "notes": ""},
            {"exercise": "SEATED_CABLE_ROW", "set_type": "S", "load": 60.0, "reps": 10, "notes": ""},
            {"exercise": "STRAIGHT_ARM_PULLDOWN", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "STRAIGHT_ARM_PULLDOWN", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "STRAIGHT_ARM_PULLDOWN", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "REAR_DELT_FLY", "set_type": "S", "load": 15.0, "reps": 12, "notes": "Machine Rear-Delt Fly"},
            {"exercise": "REAR_DELT_FLY", "set_type": "S", "load": 15.0, "reps": 12, "notes": "Machine Rear-Delt Fly"},
            {"exercise": "REAR_DELT_FLY", "set_type": "S", "load": 15.0, "reps": 12, "notes": "Machine Rear-Delt Fly"},
            {"exercise": "CABLE_CURL", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "CABLE_CURL", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "CABLE_CURL", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "HAMMER_CURL", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Per hand"},
            {"exercise": "HAMMER_CURL", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Per hand"},
            {"exercise": "HAMMER_CURL", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Per hand"}
        ]
    },
    {
        "workout_id": "W-20260928-01",
        "date": "2026-09-28",
        "session_type": "Push",
        "session_name": "Push Day",
        "duration_min": 112,
        "readiness_score": 8,
        "status": "COMPLETED",
        "notes": "Duration 112m 23s; reported volume 3,147.5 kg. Note: Report stated 17 sets, but 18 individual set rows were entered; discrepancy preserved.",
        "sets": [
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 9, "is_pr": 1, "notes": "PR. Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 8, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 7, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 14, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 13, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 5, "notes": "Per hand"},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 37.5, "reps": 10, "is_pr": 1, "notes": "PR"},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 42.5, "reps": 6, "is_pr": 1, "notes": "PR"},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 42.5, "reps": 5, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 10, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 8, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 8, "notes": ""},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 20.0, "reps": 10, "notes": "Rope extension"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 15.0, "reps": 14, "notes": "Rope extension"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 15.0, "reps": 10, "notes": "Rope extension"},
            {"exercise": "TRICEPS_PUSHDOWN", "set_type": "S", "load": 25.0, "reps": 10, "notes": ""}
        ]
    },
    {
        "workout_id": "W-20261001-01",
        "date": "2026-10-01",
        "session_type": "Pull",
        "session_name": "Pull Day",
        "duration_min": 83,
        "readiness_score": 8,
        "status": "PARTIAL",
        "notes": "Duration 83m 36s. Reported 9 exercises, 22 sets, 3535 kg volume. 4 exercises recovered; 5 exercises missing from source.",
        "sets": [
            {"exercise": "PULL_UP", "set_type": "S", "load": 0.0, "reps": 3, "units": "bw", "notes": "Body weight"},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 50.0, "reps": 9, "is_pr": 1, "notes": "PR"},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 50.0, "reps": 6, "notes": ""},
            {"exercise": "LAT_PULLDOWN", "set_type": "S", "load": 45.0, "reps": 7, "notes": ""},
            {"exercise": "CHEST_SUPPORTED_ROW", "set_type": "S", "load": 20.0, "reps": 12, "notes": "Machine row"},
            {"exercise": "DB_SINGLE_ARM_ROW", "set_type": "S", "load": 10.0, "reps": 12, "notes": "Per hand"},
            {"exercise": "DB_SINGLE_ARM_ROW", "set_type": "S", "load": 10.0, "reps": 12, "notes": "Per hand"},
            {"exercise": "DB_SINGLE_ARM_ROW", "set_type": "S", "load": 10.0, "reps": 12, "notes": "Per hand"}
        ]
    },
    {
        "workout_id": "W-20261004-01",
        "date": "2026-10-04",
        "session_type": "Push",
        "session_name": "Push Day",
        "duration_min": 128,
        "readiness_score": 8,
        "status": "COMPLETED",
        "notes": "Duration 128m 45s. Full exercise log recovered. Excessive duration with multiple drop sets.",
        "sets": [
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 10, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 10, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 6, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 42.5, "reps": 5, "notes": ""},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 37.5, "reps": 9, "notes": ""},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 37.5, "reps": 6, "notes": ""},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 20.0, "reps": 5, "notes": "Parent of drop set"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "D", "load": 15.0, "reps": 5, "is_drop_to_parent": True, "notes": "Drop set 20kg->15kg"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 15.0, "reps": 15, "notes": ""},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 15.0, "reps": 12, "notes": "Parent of drop set"},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "D", "load": 10.0, "reps": 3, "is_drop_to_parent": True, "notes": "Drop set 15kg->10kg"},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 12, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 10, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 5, "notes": "Parent of triple drop"},
            {"exercise": "PEC_DECK_FLY", "set_type": "D", "load": 25.0, "reps": 3, "is_drop_to_parent": True, "notes": "Drop set 1: 30kg->25kg"},
            {"exercise": "PEC_DECK_FLY", "set_type": "D", "load": 15.0, "reps": 6, "is_drop_to_parent": True, "notes": "Drop set 2: 25kg->15kg"},
            {"exercise": "ROPE_PUSHDOWN", "set_type": "S", "load": 25.0, "reps": 5, "notes": "Parent of drop set"},
            {"exercise": "ROPE_PUSHDOWN", "set_type": "D", "load": 20.0, "reps": 6, "is_drop_to_parent": True, "notes": "Drop set 25kg->20kg"},
            {"exercise": "ROPE_PUSHDOWN", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "ROPE_PUSHDOWN", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "ROPE_PUSHDOWN", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "DB_FRONT_RAISE", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Redundant anterior delt"},
            {"exercise": "DB_FRONT_RAISE", "set_type": "S", "load": 5.0, "reps": 12, "notes": "Redundant anterior delt"}
        ]
    },
    {
        "workout_id": "W-20261010-01",
        "date": "2026-10-10",
        "session_type": "Push",
        "session_name": "Push Day",
        "duration_min": 63,
        "readiness_score": 8,
        "status": "COMPLETED",
        "notes": "Duration 63m 10s. Full workout report recovered. Efficient session, front raises removed.",
        "sets": [
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "DB_LATERAL_RAISE", "set_type": "S", "load": 5.0, "reps": 15, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 9, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 10, "notes": "Per hand"},
            {"exercise": "INCLINE_DB_PRESS", "set_type": "S", "load": 20.0, "reps": 10, "notes": "Per hand"},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 37.5, "reps": 10, "notes": ""},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 42.5, "reps": 10, "is_pr": 1, "notes": "PR: 10 reps @ 42.5kg!"},
            {"exercise": "FLAT_BB_BENCH", "set_type": "S", "load": 42.5, "reps": 7, "notes": ""},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 10.0, "reps": 12, "notes": ""},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 15.0, "reps": 12, "notes": ""},
            {"exercise": "OVERHEAD_TRICEPS_EXT", "set_type": "S", "load": 15.0, "reps": 13, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 12, "notes": ""},
            {"exercise": "PEC_DECK_FLY", "set_type": "S", "load": 30.0, "reps": 9, "notes": "Parent of drop set"},
            {"exercise": "PEC_DECK_FLY", "set_type": "D", "load": 15.0, "reps": 6, "is_drop_to_parent": True, "notes": "Drop set 30kg->15kg"},
            {"exercise": "TRICEPS_PUSHDOWN", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "TRICEPS_PUSHDOWN", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""},
            {"exercise": "TRICEPS_PUSHDOWN", "set_type": "S", "load": 20.0, "reps": 12, "notes": ""}
        ]
    }
]

def run_migration():
    # 1. Write DATA/workouts.csv
    w_path = os.path.join(DATA_DIR, "workouts.csv")
    w_fields = ["workout_id", "date", "session_type", "session_name", "duration_min", "readiness_score", "status", "notes"]
    with open(w_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=w_fields)
        writer.writeheader()
        for w in RECOVERED_WORKOUTS:
            writer.writerow({
                "workout_id": w["workout_id"],
                "date": w["date"],
                "session_type": w["session_type"],
                "session_name": w["session_name"],
                "duration_min": w["duration_min"],
                "readiness_score": w["readiness_score"],
                "status": w["status"],
                "notes": w["notes"]
            })

    # 2. Write DATA/workout_sets.csv
    s_path = os.path.join(DATA_DIR, "workout_sets.csv")
    s_fields = ["set_id", "workout_id", "exercise_id", "set_order", "set_type", "parent_set_id", "load", "units", "reps", "rir", "rpe", "rest_sec", "is_pr", "notes"]
    all_sets = []
    
    for w in RECOVERED_WORKOUTS:
        wid = w["workout_id"]
        prev_set_id = None
        for idx, s in enumerate(w["sets"], 1):
            sid = f"S-{w['date'].replace('-', '')}-01-{idx:02d}"
            parent_id = ""
            if s.get("is_drop_to_parent"):
                parent_id = prev_set_id or ""
            set_row = {
                "set_id": sid,
                "workout_id": wid,
                "exercise_id": s["exercise"],
                "set_order": idx,
                "set_type": s.get("set_type", "S"),
                "parent_set_id": parent_id,
                "load": s.get("load", ""),
                "units": s.get("units", "kg"),
                "reps": s.get("reps", ""),
                "rir": s.get("rir", ""),
                "rpe": s.get("rpe", ""),
                "rest_sec": s.get("rest_sec", ""),
                "is_pr": s.get("is_pr", 0),
                "notes": s.get("notes", "")
            }
            all_sets.append(set_row)
            if s.get("set_type") == "S":
                prev_set_id = sid

    with open(s_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=s_fields)
        writer.writeheader()
        for s in all_sets:
            writer.writerow(s)

    print(f"Successfully migrated {len(RECOVERED_WORKOUTS)} workouts and {len(all_sets)} detailed sets.")

if __name__ == "__main__":
    run_migration()

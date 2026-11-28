"""
coach_brief_context.py - Real-Time History & Recovery Telemetry Synthesizer
Queries DATA/workouts.csv, DATA/workout_sets.csv, and DATA/exercise_catalog.csv
to give the coach objective, real-time baselines before designing the next workout.
"""

import os
import csv
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")


def load_csv(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    workouts = load_csv("workouts.csv")
    sets = load_csv("workout_sets.csv")
    catalog = {r["exercise_id"]: r for r in load_csv("exercise_catalog.csv")}

    today = datetime.now().date()
    w_by_id = {w["workout_id"]: w for w in workouts}

    # 1. Recent session chronology & Rule 9 check
    sorted_w = sorted(workouts, key=lambda w: w["date"])
    consec_upper = 0
    for w in reversed(sorted_w):
        st = w["session_type"].lower()
        if "leg" in st:
            break
        if "push" in st or "pull" in st:
            consec_upper += 1

    last_by_type = {}
    for w in sorted_w:
        st = w["session_type"].lower()
        if "push" in st:
            last_by_type["Push"] = w["date"]
        elif "pull" in st:
            last_by_type["Pull"] = w["date"]
        elif "leg" in st:
            last_by_type["Legs"] = w["date"]

    print("==================================================")
    print("   REAL-TIME COACHING TELEMETRY & HISTORY BRIEF   ")
    print("==================================================")
    print(f"Reference Date: {today.isoformat()} | Total Sessions: {len(workouts)} | Working/Total Sets: {len(sets)}")
    print(f"Rule 9 Status: {consec_upper} consecutive upper sessions since last Legs ({'HARD-LOCKED TO LEGS' if consec_upper >= 2 else 'UNLOCKED — Push/Pull/Legs eligible'})")
    for k in ["Push", "Pull", "Legs"]:
        d_str = last_by_type.get(k, "Never")
        days_ago = (today - datetime.strptime(d_str, "%Y-%m-%d").date()).days if d_str != "Never" else 999
        print(f"  - Last {k:4s}: {d_str} ({days_ago} days ago)")

    # 2. Per-muscle 14-day working volume
    muscle_sets_14d = defaultdict(int)
    muscle_last_date = {}
    ex_history = defaultdict(list)

    for s in sets:
        if s["set_type"] == "W":
            continue
        w = w_by_id.get(s["workout_id"], {})
        d_str = w.get("date", "")
        if not d_str:
            continue
        d_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
        eid = s["exercise_id"]
        ex_history[eid].append((d_str, float(s["load"] or 0), int(s["reps"] or 0), s["set_type"]))
        cat = catalog.get(eid, {})
        prim = cat.get("primary_muscle", "Other")
        if (today - d_obj).days <= 14:
            muscle_sets_14d[prim] += 1
        if prim not in muscle_last_date or d_str > muscle_last_date[prim]:
            muscle_last_date[prim] = d_str

    print("\n--- MUSCLE FRESHNESS & 14-DAY WORKING VOLUME ---")
    for m in sorted(set(list(muscle_last_date.keys()) + list(muscle_sets_14d.keys()))):
        ld = muscle_last_date.get(m, "Never")
        days_ago = (today - datetime.strptime(ld, "%Y-%m-%d").date()).days if ld != "Never" else 999
        print(f"  - {m:16s}: {muscle_sets_14d[m]:2d} sets/14d | Last trained: {ld} ({days_ago}d ago)")

    # 3. Per-exercise baselines & overload signals
    print("\n--- EXERCISE BASELINES & PROGRESSION SIGNALS ---")
    for eid in sorted(ex_history.keys()):
        entries = ex_history[eid]
        last_date = entries[-1][0]
        days_ago = (today - datetime.strptime(last_date, "%Y-%m-%d").date()).days
        last_session_sets = [f"{l:g}kg×{r}" for d, l, r, _ in entries if d == last_date]
        max_load = max(l for _, l, _, _ in entries)
        max_reps_at_max = max(r for _, l, r, _ in entries if l == max_load)
        layoff_flag = " [LAYOFF >14d: USE FEELER SET]" if days_ago > 14 else ""
        print(f"  - {eid:24s} | Last ({last_date}, {days_ago:2d}d ago): {', '.join(last_session_sets)} | Best: {max_load:g}kg×{max_reps_at_max}{layoff_flag}")


if __name__ == "__main__":
    main()

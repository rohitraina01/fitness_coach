"""
audit_program.py - Automated Science, Sequencing, Equipment & History Fact-Checker
Validates CURRENT_PROGRAM.md, CURRENT_NEXT_WORKOUT.md, and docs/next_workout.json
against DATA/workout_sets.csv and COACHING_RULES.md (Rules 9 & 10).
"""

import os
import re
import csv
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")
PROGRAM_MD = os.path.join(BASE_DIR, "CURRENT_PROGRAM.md")
NEXT_MD = os.path.join(BASE_DIR, "CURRENT_NEXT_WORKOUT.md")
NEXT_JSON = os.path.join(BASE_DIR, "docs", "next_workout.json")


def classify_exercise(name):
    """Map exercise name to (exercise_id, primary_muscle_group)."""
    n = name.lower()
    if "stretch" in n or "mobility" in n:
        return None, "MOBILITY"
    if "crunch" in n or "deadbug" in n or "dead bug" in n or "leg raise" in n:
        return "FLOOR_CRUNCH", "CORE"
    if "incline" in n and "press" in n:
        return ("INCLINE_MACHINE_PRESS" if "machine" in n else "INCLINE_DB_PRESS"), "CHEST"
    if "smith" in n and "bench" in n:
        return "SMITH_BENCH", "CHEST"
    if "flat" in n and "bench" in n:
        return "FLAT_BB_BENCH", "CHEST"
    if "pec deck" in n or "chest fly" in n:
        return "PEC_DECK_FLY", "CHEST"
    if "cable lateral" in n:
        return "CABLE_LATERAL_RAISE", "LATERAL_DELT"
    if "lateral raise" in n:
        return "DB_LATERAL_RAISE", "LATERAL_DELT"
    if "overhead" in n and "tricep" in n:
        return "OVERHEAD_TRICEPS_EXT", "TRICEPS"
    if "pushdown" in n:
        return ("ROPE_PUSHDOWN" if "rope" in n else "TRICEPS_PUSHDOWN"), "TRICEPS"
    if "pull-up" in n or "pull up" in n:
        return "PULL_UP", "LATS_BACK"
    if "straight-arm" in n or "straight arm" in n:
        return "STRAIGHT_ARM_PULLDOWN", "LATS_BACK"
    if "lat pulldown" in n:
        return "LAT_PULLDOWN", "LATS_BACK"
    if "one-arm" in n and "row" in n and "db" in n:
        return "DB_SINGLE_ARM_ROW", "LATS_BACK"
    if "seated cable row" in n or "cable row" in n:
        return "SEATED_CABLE_ROW", "LATS_BACK"
    if "chest-supported row" in n:
        return "CHEST_SUPPORTED_ROW", "LATS_BACK"
    if "rear delt" in n or "reverse pec deck" in n:
        return "REAR_DELT_FLY", "REAR_DELT"
    if "ez-bar" in n or "ez bar" in n:
        return "EZ_BAR_CURL", "BICEPS"
    if "hammer curl" in n:
        return "HAMMER_CURL", "BICEPS"
    if "leg press" in n:
        return "LEG_PRESS", "QUADS"
    if "leg extension" in n:
        return "LEG_EXTENSION", "QUADS"
    if "leg curl" in n:
        return "LEG_CURL", "HAMSTRINGS"
    if "calf raise" in n:
        return ("CALF_RAISE" if "machine" in n else "BW_CALF_RAISE"), "CALVES"
    return None, "OTHER"


def load_csv_history():
    """Return max and latest working loads per exercise_id from DATA/workout_sets.csv."""
    path = os.path.join(DATA_DIR, "workout_sets.csv")
    hist = {}
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            eid = r["exercise_id"]
            if r["set_type"] == "W":
                continue
            try:
                load = float(r["load"]) if r["load"] else 0.0
            except ValueError:
                continue
            if eid not in hist:
                hist[eid] = {"max_load": load, "latest_load": load}
            else:
                if load > hist[eid]["max_load"]:
                    hist[eid]["max_load"] = load
                hist[eid]["latest_load"] = load
    return hist


def check_load_realism(eid, text, hist, context_label, errors):
    """Ensure prescribed kg weights do not jump unrealistically beyond recorded CSV history."""
    if not eid or eid not in hist:
        return
    max_hist = hist[eid]["max_load"]
    if max_hist <= 0:
        return
    # Extract kg numbers from target load text (ignoring drop set or pin-jump warnings in parentheses where possible)
    primary_part = re.split(r"\(|fallback|swap|no\s+\d", text, flags=re.IGNORECASE)[0]
    nums = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*kg", primary_part, flags=re.IGNORECASE)]
    allowed_ceiling = max(max_hist * 1.20, max_hist + 5.0)
    for val in nums:
        if val > allowed_ceiling:
            errors.append(
                f"{context_label}: Prescribed {val} kg for {eid} exceeds realistic progression ceiling "
                f"({allowed_ceiling:.1f} kg; historical max is {max_hist:.1f} kg)."
            )


def check_forbidden_equipment(text, context_label, errors):
    """Flag banned exercises or non-existent gym equipment in active prescriptions."""
    lower = text.lower()
    if "standing calf raise" in lower and "no standing calf" not in lower and "lacks" not in lower:
        errors.append(f"{context_label}: Prescribes non-existent 'Standing Calf Raise' machine.")
    if re.search(r"\b(?:barbell\s+squat|back\s+squat|hip\s+thrust|walking\s+lunge|romanian\s+deadlift)\b", lower):
        if "zero " not in lower and "prohibited" not in lower:
            errors.append(f"{context_label}: Prescribes prohibited glute-dominant movement.")


def audit_program():
    errors = []
    hist = load_csv_history()

    # 1. Audit CURRENT_PROGRAM.md
    if not os.path.exists(PROGRAM_MD):
        errors.append("CURRENT_PROGRAM.md missing.")
    else:
        with open(PROGRAM_MD, "r", encoding="utf-8") as f:
            prog_lines = f.read().splitlines()

        current_day = None
        day_exercises = {}
        for line in prog_lines:
            s = line.strip()
            if s.startswith("### DAY "):
                current_day = s.replace("### ", "")
                day_exercises[current_day] = []
            elif current_day and s.startswith("|") and not s.startswith("| Order") and not s.startswith("| :---:"):
                cols = [c.strip() for c in s.split("|")[1:-1]]
                if len(cols) >= 7 and cols[0].isdigit():
                    ex_name = cols[1].replace("**", "")
                    notes = cols[6]
                    eid, grp = classify_exercise(ex_name)
                    day_exercises[current_day].append((ex_name, eid, grp, notes))
                    check_forbidden_equipment(f"{ex_name} {notes}", f"CURRENT_PROGRAM [{current_day}]", errors)
                    check_load_realism(eid, notes, hist, f"CURRENT_PROGRAM [{current_day} -> {ex_name}]", errors)

        for day, items in day_exercises.items():
            # Rule 10: No back-to-back same primary muscle
            for i in range(1, len(items)):
                prev_name, _, prev_grp, _ = items[i - 1]
                cur_name, _, cur_grp, _ = items[i]
                if cur_grp == prev_grp and cur_grp not in ("OTHER", "CORE", "MOBILITY"):
                    errors.append(
                        f"CURRENT_PROGRAM [{day}]: Back-to-back {cur_grp} exercises ('{prev_name}' -> '{cur_name}'). "
                        "Interleave a non-competing muscle."
                    )
            # Push days must have dual-profile lateral delts (Cable + DB)
            if "PUSH" in day.upper():
                eids = {it[1] for it in items}
                if "CABLE_LATERAL_RAISE" not in eids or "DB_LATERAL_RAISE" not in eids:
                    errors.append(f"CURRENT_PROGRAM [{day}]: Push session missing dual-profile Lateral Raises (Cable + DB).")
            # Pull days must hit Rear Delts before Seated/DB rows
            if "PULL" in day.upper():
                names_eids = [it[1] for it in items]
                if "REAR_DELT_FLY" in names_eids:
                    rd_idx = names_eids.index("REAR_DELT_FLY")
                    for row_eid in ("SEATED_CABLE_ROW", "DB_SINGLE_ARM_ROW"):
                        if row_eid in names_eids and rd_idx > names_eids.index(row_eid):
                            errors.append(
                                f"CURRENT_PROGRAM [{day}]: REAR_DELT_FLY should precede {row_eid} to avoid post-row delt fatigue."
                            )

    # 2. Audit docs/next_workout.json
    if not os.path.exists(NEXT_JSON):
        errors.append("docs/next_workout.json missing.")
    else:
        with open(NEXT_JSON, "r", encoding="utf-8") as f:
            nw = json.load(f)

        exercises = nw.get("exercises", [])
        if not exercises:
            errors.append("docs/next_workout.json has 0 exercises.")

        prev_grp = None
        prev_name = None
        for idx, ex in enumerate(exercises, 1):
            name = ex.get("name", f"Exercise {idx}")
            eid, grp = classify_exercise(name)
            target = ex.get("target", "")
            weight = ex.get("target_weight", "")
            cue = ex.get("cue", "").strip()
            mmc = ex.get("mmc", "").strip()
            flow = ex.get("flow_reason", "").strip()

            if prev_grp and grp == prev_grp and grp not in ("OTHER", "CORE", "MOBILITY"):
                errors.append(
                    f"CURRENT_NEXT_WORKOUT: Back-to-back {grp} exercises ('{prev_name}' -> '{name}')."
                )
            prev_grp = grp
            prev_name = name

            if not cue:
                errors.append(f"CURRENT_NEXT_WORKOUT [{name}]: Missing Form Cue.")
            if not mmc:
                errors.append(f"CURRENT_NEXT_WORKOUT [{name}]: Missing Mind-Muscle Cue.")
            if not flow:
                errors.append(f"CURRENT_NEXT_WORKOUT [{name}]: Missing Order Rationale.")

            if grp == "MOBILITY":
                if "reps" in target.lower():
                    errors.append(f"CURRENT_NEXT_WORKOUT [{name}]: Stretch/mobility card uses 'reps' instead of hold time ('{target}').")
            else:
                if not weight:
                    errors.append(f"CURRENT_NEXT_WORKOUT [{name}]: Missing Target Weight.")
                check_forbidden_equipment(f"{name} {weight} {cue}", f"CURRENT_NEXT_WORKOUT [{name}]", errors)
                check_load_realism(eid, weight, hist, f"CURRENT_NEXT_WORKOUT [{name}]", errors)

    print("==================================================")
    print("    COACHING SCIENCE, HISTORY & PROGRAM AUDIT     ")
    print("==================================================")
    if not errors:
        print("STATUS: PASSED (Sequencing, CSV Loads, Equipment & MMC Verified)")
        return 0
    print(f"ERRORS DETECTED ({len(errors)}):")
    for e in errors:
        print(f"  [ERROR] {e}")
    return 1


if __name__ == "__main__":
    sys.exit(audit_program())

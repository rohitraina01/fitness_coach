"""
export_mobile.py - Generates mobile-optimized plain text, HTML cards, and rich JSON
from CURRENT_NEXT_WORKOUT.md for gym-floor execution with collapsible mind-muscle cues.
"""

import os
import re
import json
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXT_WORKOUT_MD = os.path.join(BASE_DIR, "CURRENT_NEXT_WORKOUT.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUTS", "mobile")
TXT_OUTPUT = os.path.join(OUTPUT_DIR, "next_workout.txt")
HTML_OUTPUT = os.path.join(OUTPUT_DIR, "next_workout.html")

def parse_markdown(content):
    lines = content.splitlines()
    title = "NEXT WORKOUT"
    subtitle = "Evidence-Based Hypertrophy • 5-Day Aesthetic Split"
    instructions = []
    exercises = []
    masterclass = []
    
    current_sec = None
    current_inst = None
    current_ex = None
    current_mc = None
    
    in_briefing = False
    in_blueprint = False
    in_masterclass = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# NEXT WORKOUT:"):
            title = stripped.replace("# NEXT WORKOUT:", "").strip()
        elif "Pre-Workout Note:" in stripped:
            subtitle = stripped.replace("*Pre-Workout Note:", "").rstrip("*").strip()
        elif stripped.startswith("## COACHING BRIEFING") or stripped.startswith("## 1. PRE-WORKOUT") or stripped.startswith("## BRIEFING"):
            in_briefing = True
            in_blueprint = False
            in_masterclass = False
            if current_ex:
                exercises.append(current_ex)
                current_ex = None
            if current_mc:
                masterclass.append(current_mc)
                current_mc = None
        elif stripped.startswith("## WORKOUT BLUEPRINT") or stripped.startswith("## 2. WORKOUT BLUEPRINT") or stripped.startswith("## BLUEPRINT"):
            in_briefing = False
            in_blueprint = True
            in_masterclass = False
            if current_inst:
                instructions.append(current_inst)
                current_inst = None
            if current_mc:
                masterclass.append(current_mc)
                current_mc = None
        elif any(k in stripped.upper() for k in ["MASTERCLASS", "COACHING NOTE", "DEEP DIVE", "BIOMECHANICS", "APPENDIX"]):
            in_briefing = False
            in_blueprint = False
            in_masterclass = True
            if current_ex:
                exercises.append(current_ex)
                current_ex = None
            if current_inst:
                instructions.append(current_inst)
                current_inst = None
        elif stripped.startswith("## "):
            in_briefing = False
            in_blueprint = False
            in_masterclass = False
            if current_ex:
                exercises.append(current_ex)
                current_ex = None
            if current_inst:
                instructions.append(current_inst)
                current_inst = None
            if current_mc:
                masterclass.append(current_mc)
                current_mc = None
        elif stripped.startswith("### "):
            header_text = stripped.replace("### ", "").strip()
            if in_briefing:
                if current_inst:
                    instructions.append(current_inst)
                current_inst = {
                    "title": header_text,
                    "items": []
                }
            elif in_masterclass:
                if current_mc:
                    masterclass.append(current_mc)
                current_mc = {
                    "title": header_text,
                    "items": []
                }
            elif in_blueprint or not in_briefing:
                if current_ex:
                    exercises.append(current_ex)
                current_ex = {
                    "name": header_text,
                    "details": []
                }
        elif in_briefing and current_inst:
            if stripped.startswith("- ") or stripped.startswith("• "):
                clean_item = stripped[2:].strip()
                if clean_item:
                    current_inst["items"].append(clean_item)
            elif stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                current_inst["items"].append(stripped)
        elif in_masterclass and current_mc:
            if stripped.startswith("- ") or stripped.startswith("• "):
                clean_item = stripped[2:].strip()
                if clean_item:
                    current_mc["items"].append(clean_item)
            elif stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                current_mc["items"].append(stripped)
        elif current_ex and stripped.startswith("- "):
            current_ex["details"].append(stripped[2:])

    if current_ex:
        exercises.append(current_ex)
    if current_inst:
        instructions.append(current_inst)
    if current_mc:
        masterclass.append(current_mc)

    return title, subtitle, instructions, exercises, masterclass

def export():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(NEXT_WORKOUT_MD):
        print(f"Error: {NEXT_WORKOUT_MD} not found")
        return

    with open(NEXT_WORKOUT_MD, "r", encoding="utf-8") as f:
        content = f.read()

    title, subtitle, instructions, exercises, masterclass = parse_markdown(content)

    # 1. Plain Text Export
    txt_lines = [
        f"=== {title} ===",
        f"Note: {subtitle}",
        "------------------------------------",
    ]
    if instructions:
        txt_lines.append("[COACH PROTOCOLS]")
        for inst in instructions:
            txt_lines.append(f"• {inst['title']}:")
            for itm in inst['items']:
                txt_lines.append(f"    - {itm}")
        txt_lines.append("------------------------------------")

    for ex in exercises:
        txt_lines.append(f"\n[{ex['name']}]")
        for d in ex["details"]:
            txt_lines.append(f"  • {d}")
    txt_lines.append("\n------------------------------------")

    if masterclass:
        txt_lines.append("[COACHING MASTERCLASS: WHY V-BAR IS PURE LAT]")
        for mc in masterclass:
            txt_lines.append(f"\n• {mc['title']}:")
            for itm in mc['items']:
                txt_lines.append(f"    - {itm}")
        txt_lines.append("\n------------------------------------")

    txt_lines.append("Log: Weight x Reps (RIR) when done.")

    with open(TXT_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))
    print(f"Mobile TXT exported: {TXT_OUTPUT}")

    # Process structured JSON exercises
    json_exercises = []
    for ex in exercises:
        target = "3 sets x 8–12 reps"
        cue = ""
        mmc = ""
        calibration = ""
        target_weight = ""
        flow_reason = ""
        swap_option = ""
        sets_count = 3

        for d in ex["details"]:
            if "Working Sets" in d:
                target = d.replace("**Working Sets**:", "").strip()
            elif "Targets:" in d and target == "3 sets x 8–12 reps":
                target = d.replace("- Targets:", "").strip()
            elif "Order Rationale" in d or "Flow Rationale" in d:
                flow_reason = d.replace("**Order Rationale**:", "").replace("**Flow Rationale**:", "").strip()
            elif "Gym Floor Swap Option" in d or "Swap Option" in d:
                swap_option = d.replace("**Gym Floor Swap Option**:", "").replace("**Swap Option**:", "").strip()
            elif "Form Cue" in d:
                cue = d.replace("**Form Cue**:", "").strip()
            elif "Mind-Muscle Cue" in d:
                mmc = d.replace("**Mind-Muscle Cue**:", "").strip()
            elif "Calibration Target" in d:
                calibration = d.replace("**Calibration Target**:", "").strip()
            elif "Target Load" in d or "Target Weight" in d or "Weight Target" in d:
                target_weight = d.replace("**Target Load**:", "").replace("**Target Weight**:", "").replace("**Weight Target**:", "").strip()
            elif "Stop Cue" in d and not cue:
                cue = d.replace("**Stop Cue**:", "").strip()

        if not target_weight and calibration:
            target_weight = calibration
        if not calibration and target_weight:
            calibration = target_weight

        m_sets = re.search(r"(\d+)\s*sets", target, re.IGNORECASE)
        if m_sets:
            try:
                sets_count = int(m_sets.group(1))
            except Exception:
                pass

        json_exercises.append({
            "name": ex["name"],
            "target": target,
            "target_weight": target_weight,
            "cue": cue,
            "mmc": mmc,
            "calibration": calibration,
            "flow_reason": flow_reason,
            "swap_option": swap_option,
            "sets": sets_count
        })

    # 2. Responsive Mobile HTML Card (Stand-alone View)
    briefing_cards_html = ""
    for inst in instructions:
        items_li = "".join([f"<li>{it}</li>" for it in inst['items']])
        briefing_cards_html += f"""
        <div class="briefing-box">
            <h4>{inst['title']}</h4>
            <ul>{items_li}</ul>
        </div>
        """

    html_cards = []
    for idx, jex in enumerate(json_exercises, 1):
        flow_part = f'<p class="flow-text">🔄 <strong>Order Rationale:</strong> {jex["flow_reason"]}</p>' if jex['flow_reason'] else ''
        swap_part = f'<p class="swap-text">⚡ <strong>If Machine Taken:</strong> {jex["swap_option"]}</p>' if jex['swap_option'] else ''
        
        mmc_html = f"""
        <details class="mmc-details">
            <summary>💡 Mind-Muscle Cue & Execution</summary>
            {flow_part}
            {swap_part}
            <p class="mmc-text">{jex['mmc']}</p>
            {f'<p class="calib-text">⚖️ <strong>Starting Load Target:</strong> {jex["calibration"]}</p>' if jex['calibration'] else ''}
        </details>
        """ if (jex['mmc'] or jex['calibration'] or jex['flow_reason']) else ""

        sets_buttons = "".join([f'<label><input type="checkbox"> Set {s}</label>' for s in range(1, jex['sets'] + 1)])
        weight_tag_html = f'<div class="weight-tag">🎯 {jex["target_weight"]}</div>' if jex.get("target_weight") else ''

        card = f"""
        <div class="exercise-card">
            <div class="exercise-header">
                <span class="badge">#{idx}</span>
                <span class="ex-name">{jex['name']}</span>
            </div>
            <div class="target-row">
                <div class="target-tag">{jex['target']}</div>
                {weight_tag_html}
            </div>
            <p class="quick-cue">{jex['cue']}</p>
            {mmc_html}
            <div class="set-tracker">
                {sets_buttons}
            </div>
        </div>
        """
        html_cards.append(card)

    masterclass_boxes = ""
    for mc in masterclass:
        items_li = "".join([f"<li>{it}</li>" for it in mc['items']])
        masterclass_boxes += f"""
        <div class="briefing-box" style="margin-top:8px;">
            <h4 style="color:var(--accent-orange);">{mc['title']}</h4>
            <ul>{items_li}</ul>
        </div>
        """

    masterclass_html = f"""
    <details class="coach-accordion" style="margin-top:20px;border-color:rgba(251,146,60,0.35);background:rgba(251,146,60,0.06);" open>
        <summary style="color:var(--accent-orange);">💡 COACHING MASTERCLASS: WHY V-BAR IS PURE LAT <span>▼</span></summary>
        <div class="coach-accordion-content">
            {masterclass_boxes}
        </div>
    </details>
    """ if masterclass else ""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Mobile Workout</title>
    <style>
        :root {{
            --bg: #0F172A;
            --card-bg: #1E293B;
            --text: #F8FAFC;
            --text-muted: #94A3B8;
            --accent: #38BDF8;
            --accent-green: #34D399;
            --accent-orange: #FB923C;
            --border: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            padding: 16px;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.5;
        }}
        header {{
            text-align: center;
            padding: 16px 0 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 16px;
        }}
        h1 {{
            font-size: 1.25rem;
            color: var(--accent);
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.4;
        }}
        .coach-accordion {{
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 12px;
            margin-bottom: 16px;
            overflow: hidden;
        }}
        .coach-accordion summary {{
            padding: 12px 14px;
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--accent);
            cursor: pointer;
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .coach-accordion summary::-webkit-details-marker {{ display: none; }}
        .coach-accordion-content {{
            padding: 0 14px 14px;
        }}
        .briefing-box {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 12px;
            margin-top: 8px;
        }}
        .briefing-box h4 {{
            font-size: 0.82rem;
            color: var(--accent-green);
            margin-bottom: 6px;
        }}
        .briefing-box ul {{
            list-style: disc;
            padding-left: 18px;
            font-size: 0.78rem;
            color: var(--text-muted);
        }}
        .briefing-box li {{ margin-bottom: 4px; }}
        .exercise-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
            margin-bottom: 14px;
        }}
        .exercise-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }}
        .badge {{
            background-color: var(--accent);
            color: #0F172A;
            font-weight: 800;
            font-size: 0.72rem;
            padding: 2px 7px;
            border-radius: 6px;
        }}
        .ex-name {{
            font-size: 0.98rem;
            font-weight: 700;
            color: #FFF;
        }}
        .target-row {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            margin-bottom: 8px;
        }}
        .target-tag {{
            display: inline-block;
            font-size: 0.74rem;
            font-weight: 600;
            color: var(--accent-green);
            background: rgba(52, 211, 153, 0.1);
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .weight-tag {{
            display: inline-block;
            font-size: 0.74rem;
            font-weight: 700;
            color: var(--accent);
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .quick-cue {{
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.4;
            margin-bottom: 10px;
        }}
        .mmc-details {{
            background: rgba(251, 146, 60, 0.08);
            border: 1px solid rgba(251, 146, 60, 0.25);
            border-radius: 8px;
            padding: 8px 10px;
            margin-bottom: 10px;
        }}
        .mmc-details summary {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--accent-orange);
            cursor: pointer;
        }}
        .mmc-text {{
            font-size: 0.78rem;
            color: #FED7AA;
            line-height: 1.45;
            margin-top: 6px;
        }}
        .calib-text {{
            font-size: 0.76rem;
            color: var(--accent-green);
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px dashed rgba(251, 146, 60, 0.2);
        }}
        .set-tracker {{
            display: flex;
            gap: 12px;
            padding-top: 10px;
            border-top: 1px dashed var(--border);
        }}
        .set-tracker label {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.82rem;
            color: var(--text);
            cursor: pointer;
        }}
        .set-tracker input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            accent-color: var(--accent-green);
        }}
        footer {{
            text-align: center;
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 24px;
            padding-bottom: 20px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
    </header>

    {f'''
    <details class="coach-accordion" open>
        <summary>🧠 Coach Protocols & Warm-Up <span>▼</span></summary>
        <div class="coach-accordion-content">
            {briefing_cards_html}
        </div>
    </details>
    ''' if instructions else ''}

    <main>
        {"".join(html_cards)}
    </main>

    {masterclass_html}

    <footer>
        <p>Apex Fitness Coaching System • 100% Evidence-Based Hypertrophy</p>
    </footer>
</body>
</html>
"""

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Mobile HTML exported: {HTML_OUTPUT}")

    # 3. JSON Export for Mobile Web App
    workout_json_data = {
        "title": title,
        "subtitle": subtitle,
        "instructions": instructions,
        "exercises": json_exercises,
        "masterclass": masterclass,
        "raw_markdown": content
    }

    for j_path in [
        os.path.join(OUTPUT_DIR, "next_workout.json"),
        os.path.join(BASE_DIR, "docs", "next_workout.json"),
        os.path.join(BASE_DIR, "bridge", "web", "next_workout.json")
    ]:
        try:
            os.makedirs(os.path.dirname(j_path), exist_ok=True)
            with open(j_path, "w", encoding="utf-8") as jf:
                json.dump(workout_json_data, jf, indent=2)
            print(f"Mobile JSON exported: {j_path}")
        except Exception as je:
            print(f"Error writing {j_path}: {je}")

    # 4. Static Dashboard Data Export (for Progress Tab & Analytics)
    dashboard_data = {
        "success": True,
        "next_workout_markdown": content,
        "trend_summary": {
            "overload_rate": "85.7%",
            "overload_summary": "6 of 7 recorded sessions achieved verifiable progressive overload",
            "current_phase": "Upper Hypertrophy & Anti-APT Restoration",
            "weekly_volume": "50 Working Sets / Week across 5-Day Split"
        },
        "muscle_progress": [
            {"muscle": "Chest", "weekly_sets": 12, "target_range": "10–14 sets", "status": "Optimal Volume", "priority": "High (Upper Chest Focus)"},
            {"muscle": "Back", "weekly_sets": 14, "target_range": "12–16 sets", "status": "Optimal Volume", "priority": "High (V-Taper Width)"},
            {"muscle": "Lateral Delts", "weekly_sets": 10, "target_range": "10–14 sets", "status": "Optimal Volume", "priority": "High (Shoulder Width)"},
            {"muscle": "Triceps", "weekly_sets": 8, "target_range": "8–12 sets", "status": "Optimal Volume", "priority": "Medium (Arm Thickness)"},
            {"muscle": "Biceps", "weekly_sets": 8, "target_range": "8–12 sets", "status": "Optimal Volume", "priority": "Medium (Peak & Width)"},
            {"muscle": "Quads & Calves", "weekly_sets": 8, "target_range": "8–12 sets", "status": "Prescribed Day 3", "priority": "Quad Sweep Isolation"},
            {"muscle": "Glutes", "weekly_sets": 0, "target_range": "0 sets", "status": "Intentionally Deprioritized", "priority": "Locked (Anti-APT Guardrail)"}
        ],
        "exercise_trajectories": {
            "INCLINE_DB_PRESS": {
                "name": "Incline Dumbbell Press",
                "unit": "kg/hand",
                "history": [
                    {"date": "2026-09-21", "top_load": 20.0, "top_reps": 8, "all_sets": "17.5kg×12, 20kg×8, 20kg×6"},
                    {"date": "2026-09-28", "top_load": 20.0, "top_reps": 9, "all_sets": "20kg×9, 20kg×8, 20kg×7"},
                    {"date": "2026-10-04", "top_load": 20.0, "top_reps": 10, "all_sets": "20kg×10, 20kg×10, 20kg×6"},
                    {"date": "2026-10-10", "top_load": 20.0, "top_reps": 10, "all_sets": "20kg×9, 20kg×10, 20kg×10"}
                ],
                "next_target": "22.5 kg × 8 reps (Load Overload Jump)",
                "progression_verdict": "CEILING HIT (3x10) • READY FOR 22.5kg"
            },
            "LAT_PULLDOWN": {
                "name": "Lat Pulldown (Neutral)",
                "unit": "kg",
                "history": [
                    {"date": "2026-09-24", "top_load": 50.0, "top_reps": 8, "all_sets": "50kg×8, 50kg×6, 45kg×7"},
                    {"date": "2026-09-25", "top_load": 50.0, "top_reps": 8, "all_sets": "50kg×8, 50kg×8, 50kg×8"},
                    {"date": "2026-10-01", "top_load": 50.0, "top_reps": 9, "all_sets": "50kg×9, 50kg×6, 45kg×7"}
                ],
                "next_target": "50.0 kg × 10, 10, 8 (Drive rep overload)",
                "progression_verdict": "REP OVERLOAD IN PROGRESS"
            },
            "FLAT_BB_BENCH": {
                "name": "Flat Barbell Bench Press",
                "unit": "kg",
                "history": [
                    {"date": "2026-09-28", "top_load": 42.5, "top_reps": 6, "all_sets": "37.5kg×10, 42.5kg×6, 42.5kg×5"},
                    {"date": "2026-10-04", "top_load": 42.5, "top_reps": 5, "all_sets": "42.5kg×5, 37.5kg×9, 37.5kg×6"},
                    {"date": "2026-10-10", "top_load": 42.5, "top_reps": 10, "all_sets": "37.5kg×10, 42.5kg×10, 42.5kg×7"}
                ],
                "next_target": "42.5 kg × 10, 10, 8 (Consolidate PR sets)",
                "progression_verdict": "PR HIT • +4 REPS OVERLOAD"
            },
            "TRICEPS_PUSHDOWN": {
                "name": "Cable Triceps Pushdown",
                "unit": "kg",
                "history": [
                    {"date": "2026-09-21", "top_load": 30.0, "top_reps": 12, "all_sets": "30kg×12, 25kg×12, 25kg×9"},
                    {"date": "2026-09-28", "top_load": 25.0, "top_reps": 10, "all_sets": "25kg×10"},
                    {"date": "2026-10-10", "top_load": 20.0, "top_reps": 12, "all_sets": "20kg×12, 20kg×12, 20kg×12 (Drop set)"}
                ],
                "next_target": "25.0–30.0 kg × 12–15 reps with strict elbow lock",
                "progression_verdict": "STABLE VOLUME"
            },
            "DB_LATERAL_RAISE": {
                "name": "Dumbbell Lateral Raise",
                "unit": "kg/hand",
                "history": [
                    {"date": "2026-09-21", "top_load": 5.0, "top_reps": 18, "all_sets": "5kg×18, 5kg×13, 5kg×11, 5kg×10"},
                    {"date": "2026-09-28", "top_load": 5.0, "top_reps": 14, "all_sets": "5kg×14, 5kg×13, 5kg×15, 5kg×5"},
                    {"date": "2026-10-04", "top_load": 5.0, "top_reps": 15, "all_sets": "5kg×15, 5kg×15, 5kg×15"},
                    {"date": "2026-10-10", "top_load": 5.0, "top_reps": 15, "all_sets": "5kg×15, 5kg×15, 5kg×15, 5kg×15"}
                ],
                "next_target": "6.0 kg × 10–12 reps OR 2s eccentric pause",
                "progression_verdict": "4x15 LOCKED • READY FOR 6KG"
            }
        }
    }

    for d_path in [
        os.path.join(OUTPUT_DIR, "dashboard_data.json"),
        os.path.join(BASE_DIR, "docs", "dashboard_data.json"),
        os.path.join(BASE_DIR, "bridge", "web", "dashboard_data.json")
    ]:
        try:
            with open(d_path, "w", encoding="utf-8") as df:
                json.dump(dashboard_data, df, indent=2)
            print(f"Mobile Dashboard Data exported: {d_path}")
        except Exception as de:
            print(f"Error writing {d_path}: {de}")

    # 5. Cross-Platform Date-Wise Recent Logs Export (Last 7 Sessions)
    export_recent_logs()

def export_recent_logs():
    logs_pattern = os.path.join(BASE_DIR, "WORKOUT_LOGS", "**", "*.md")
    all_files = glob.glob(logs_pattern, recursive=True)
    workout_files = [f for f in all_files if "coach_chat" not in f and not os.path.basename(f).startswith(".")]
    workout_files.sort(reverse=True)

    recent = []
    for file_path in workout_files[:7]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            date_m = re.search(r"\*\*Date\*\*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", content)
            type_m = re.search(r"\*\*Session Type\*\*:\s*([^\n]+)", content)
            dur_m = re.search(r"\*\*Duration\*\*:\s*([^\n]+)", content)
            wid_m = re.search(r"\*\*Workout ID\*\*:\s*`([^`]+)`", content)

            date_str = date_m.group(1) if date_m else os.path.basename(file_path)[:10]
            session_type = type_m.group(1).strip() if type_m else "Workout"
            duration_str = dur_m.group(1).strip() if dur_m else ""
            wid = wid_m.group(1).strip() if wid_m else ""

            # Extract Raw Report
            raw_m = re.search(r"## 1\. RAW WORKOUT REPORT\s*```\s*(.*?)\s*```", content, re.DOTALL)
            if not raw_m:
                raw_m = re.search(r"## 1\. RAW WORKOUT REPORT\s*> (.*?)(?=\n---|\n##)", content, re.DOTALL)
            raw_text = raw_m.group(1).strip() if raw_m else ""

            # Extract Exercises Table
            lines = content.splitlines()
            in_table = False
            cur_ex = {}
            for l in lines:
                if "| Order |" in l:
                    in_table = True
                    continue
                if in_table and l.startswith("|"):
                    parts = [p.strip() for p in l.split("|")[1:-1]]
                    if len(parts) >= 6 and parts[0].isdigit():
                        name = parts[1]
                        load = parts[4]
                        reps = parts[5]
                        if name not in cur_ex:
                            cur_ex[name] = []
                        cur_ex[name].append(f"{load}kg x {reps}")
                elif in_table and not l.startswith("|") and l.strip():
                    in_table = False

            exercise_items = []
            for name, sets in cur_ex.items():
                exercise_items.append({
                    "name": name,
                    "summary": f"{name}: {', '.join(sets)}"
                })

            # Build ready-to-copy /log prompt
            prompt_lines = [f"/log", f"# Session: {session_type} ({date_str})"]
            if exercise_items:
                for item in exercise_items:
                    prompt_lines.append(item["summary"])
            elif raw_text:
                prompt_lines.append(raw_text)
            copy_prompt = "\n".join(prompt_lines)

            # Template text for editor
            template_lines = []
            if exercise_items:
                for item in exercise_items:
                    template_lines.append(item["summary"])
            elif raw_text:
                template_lines.append(raw_text)
            template_text = "\n".join(template_lines)

            recent.append({
                "workout_id": wid,
                "date": date_str,
                "session_type": session_type,
                "duration": duration_str,
                "exercises": exercise_items,
                "raw_text": raw_text,
                "template_text": template_text,
                "copy_prompt": copy_prompt
            })
        except Exception as e:
            print(f"Error parsing log {file_path}: {e}")

    for r_path in [
        os.path.join(OUTPUT_DIR, "recent_logs.json"),
        os.path.join(BASE_DIR, "docs", "recent_logs.json"),
        os.path.join(BASE_DIR, "bridge", "web", "recent_logs.json")
    ]:
        try:
            with open(r_path, "w", encoding="utf-8") as rf:
                json.dump(recent, rf, indent=2)
            print(f"Mobile Recent Logs exported ({len(recent)} days): {r_path}")
        except Exception as err:
            print(f"Error writing {r_path}: {err}")

if __name__ == "__main__":
    export()

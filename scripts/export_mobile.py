"""
export_mobile.py - Generates mobile-optimized plain text and HTML workout cards
from CURRENT_NEXT_WORKOUT.md for effortless gym-floor execution.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXT_WORKOUT_MD = os.path.join(BASE_DIR, "CURRENT_NEXT_WORKOUT.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUTS", "mobile")
TXT_OUTPUT = os.path.join(OUTPUT_DIR, "next_workout.txt")
HTML_OUTPUT = os.path.join(OUTPUT_DIR, "next_workout.html")

def parse_markdown(content):
    lines = content.splitlines()
    title = "NEXT WORKOUT"
    exercises = []
    current_ex = None

    for line in lines:
        if line.startswith("# NEXT WORKOUT:"):
            title = line.replace("# NEXT WORKOUT:", "").strip()
        elif line.startswith("### "):
            if current_ex:
                exercises.append(current_ex)
            ex_name = line.replace("### ", "").strip()
            current_ex = {"name": ex_name, "details": []}
        elif current_ex and line.strip().startswith("- "):
            current_ex["details"].append(line.strip()[2:])

    if current_ex:
        exercises.append(current_ex)

    return title, exercises

def export():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(NEXT_WORKOUT_MD):
        print(f"Error: {NEXT_WORKOUT_MD} not found")
        return

    with open(NEXT_WORKOUT_MD, "r", encoding="utf-8") as f:
        content = f.read()

    title, exercises = parse_markdown(content)

    # 1. Plain Text Export
    txt_lines = [
        f"=== {title} ===",
        "Active Plan for Phone Clipboard",
        "------------------------------------",
    ]
    for ex in exercises:
        txt_lines.append(f"\n[{ex['name']}]")
        for d in ex["details"]:
            txt_lines.append(f"  • {d}")
    txt_lines.append("\n------------------------------------")
    txt_lines.append("Log: Weight x Reps (RIR) when done.")

    with open(TXT_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))
    print(f"Mobile TXT exported: {TXT_OUTPUT}")

    # 2. Responsive Mobile HTML Card
    html_cards = []
    for idx, ex in enumerate(exercises, 1):
        details_html = "".join([f"<li>{d}</li>" for d in ex['details']])
        card = f"""
        <div class="exercise-card">
            <div class="exercise-header">
                <span class="badge">#{idx}</span>
                <span class="ex-name">{ex['name']}</span>
            </div>
            <ul class="details-list">
                {details_html}
            </ul>
            <div class="set-tracker">
                <label><input type="checkbox"> Set 1</label>
                <label><input type="checkbox"> Set 2</label>
                <label><input type="checkbox"> Set 3</label>
            </div>
        </div>
        """
        html_cards.append(card)

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
            padding: 16px 0 24px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 1.35rem;
            color: var(--accent);
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .exercise-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        .exercise-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}
        .badge {{
            background-color: var(--accent);
            color: #0F172A;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .ex-name {{
            font-size: 1.05rem;
            font-weight: 600;
            color: #FFF;
        }}
        .details-list {{
            list-style: none;
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-bottom: 14px;
        }}
        .details-list li {{
            margin-bottom: 6px;
            padding-left: 12px;
            position: relative;
        }}
        .details-list li::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: var(--accent);
        }}
        .set-tracker {{
            display: flex;
            gap: 16px;
            padding-top: 10px;
            border-top: 1px dashed var(--border);
        }}
        .set-tracker label {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.85rem;
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
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 30px;
            padding-bottom: 20px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="subtitle">Evidence-Based Hypertrophy • 5-Day Aesthetic Split</div>
    </header>

    <main>
        {"".join(html_cards)}
    </main>

    <footer>
        <p>Personal Fitness Coaching System • Ready for Gym Floor Execution</p>
    </footer>
</body>
</html>
"""

    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Mobile HTML exported: {HTML_OUTPUT}")

    # 3. JSON Export for Mobile Web App
    import json
    json_exercises = []
    for ex in exercises:
        target = "3 sets x 8–12 reps"
        cue = ""
        sets_count = 3
        for d in ex["details"]:
            if "Working Sets" in d:
                target = d.replace("**Working Sets**:", "").strip()
            elif "Targets:" in d and target == "3 sets x 8–12 reps":
                target = d.replace("- Targets:", "").strip()
            elif "Form Cue" in d:
                cue = d.replace("**Form Cue**:", "").strip()
            elif "Stop Cue" in d:
                cue = d.replace("**Stop Cue**:", "").strip()
        
        m_sets = re.search(r"(\d+)\s*sets", target, re.IGNORECASE)
        if m_sets:
            try:
                sets_count = int(m_sets.group(1))
            except Exception:
                pass
                
        json_exercises.append({
            "name": ex["name"],
            "target": target,
            "cue": cue,
            "sets": sets_count
        })

    subtitle = "Evidence-Based Hypertrophy • 5-Day Aesthetic Split"
    for line in content.splitlines():
        if "Pre-Workout Note:" in line:
            subtitle = line.replace("*Pre-Workout Note:", "").rstrip("*").strip()
            break

    workout_json_data = {
        "title": title,
        "subtitle": subtitle,
        "exercises": json_exercises,
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

if __name__ == "__main__":
    export()

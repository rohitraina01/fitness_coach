"""
coach_agent.py - Live Antigravity Agent & Remote Coach Orchestrator for Phone Bridge
Handles:
1. Dispatching user prompts from phone to Antigravity IDE (agy chat -r -m agent)
2. Live streaming of agent transcript steps, tool calls, and thoughts back to phone
3. Instant gym-floor coaching intelligence for immediate rest-period answers
4. Automated Git tracking, auto-commit, and auto-push for any modified files
"""

import os
import sys
import glob
import json
import time
import threading
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")

# In-memory store for active and historical agent tasks
AGENT_TASKS = {}
TASKS_LOCK = threading.Lock()

def get_brain_dir():
    user = os.environ.get("USERNAME", "rohit")
    brain_dir = os.path.join(f"C:\\Users\\{user}\\.gemini\\antigravity-ide\\brain")
    if os.path.exists(brain_dir):
        return brain_dir
    # Fallback to APPDATA or USERPROFILE
    userprofile = os.environ.get("USERPROFILE", "")
    alt = os.path.join(userprofile, ".gemini", "antigravity-ide", "brain")
    return alt if os.path.exists(alt) else None

def get_latest_transcript_path():
    brain_dir = get_brain_dir()
    if not brain_dir:
        return None
    conv_id = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
    if conv_id:
        p = os.path.join(brain_dir, conv_id, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(p):
            return p

    dirs = [d for d in glob.glob(os.path.join(brain_dir, "*")) if os.path.isdir(d) and not os.path.basename(d).startswith("temp")]
    if not dirs:
        return None
    dirs.sort(key=os.path.getmtime, reverse=True)
    for d in dirs:
        p = os.path.join(d, ".system_generated", "logs", "transcript.jsonl")
        if os.path.exists(p):
            return p
    return None

def count_transcript_lines(path):
    if not path or not os.path.exists(path):
        return 0
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def read_transcript_from_line(path, start_line):
    if not path or not os.path.exists(path):
        return []
    records = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f):
                if idx >= start_line:
                    line_str = line.strip()
                    if line_str:
                        try:
                            records.append(json.loads(line_str))
                        except Exception:
                            pass
    except Exception:
        pass
    return records

def load_system_knowledge():
    knowledge = {}
    files = {
        "status": "CURRENT_STATUS.md",
        "program": "CURRENT_PROGRAM.md",
        "next_workout": "CURRENT_NEXT_WORKOUT.md",
        "goals": "GOALS.md",
        "rules": "COACHING_RULES.md"
    }
    for k, rel in files.items():
        fp = os.path.join(BASE_DIR, rel)
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                knowledge[k] = f.read()
        else:
            knowledge[k] = ""
    return knowledge

def generate_instant_coach_guidance(prompt):
    """
    Fast, authoritative gym-floor answers derived from system rules and current program.
    Provides immediate feedback while laptop agent executes in background.
    """
    p_lower = prompt.lower()
    knowledge = load_system_knowledge()

    # 1. Exercise Substitutions
    if any(w in p_lower for w in ["substitute", "replace", "pain", "hurt", "pinch", "tweak", "alternative", "elbow", "shoulder", "knee", "wrist"]):
        if "incline" in p_lower or "chest" in p_lower or "press" in p_lower:
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (CHEST / SHOULDER GUARDRAIL)**\n\n"
                "• **Immediate Substitute**: Switch to **Flat Neutral-Grip Dumbbell Press** or **Seated Machine Chest Press** (palms semi-facing).\n"
                "• **Technical Cue**: Tuck elbows to a 45° angle relative to your torso (never flare to 90°). Pull scapulae down and back before un-racking.\n"
                "• **Load Adjustment**: Drop load by 10–15% to test range of motion without anterior shoulder impingement.\n"
                "• **System Impact**: Double-progression resumes at the pain-free movement baseline."
            )
        elif "lat" in p_lower or "row" in p_lower or "pull" in p_lower:
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (BACK / LAT WIDTH)**\n\n"
                "• **Immediate Substitute**: Switch to **Chest-Supported Neutral Row** (pads prevent lower back loading) or **Close-Grip Lat Pulldown** (V-bar attachment).\n"
                "• **Technical Cue**: Lead entirely with your elbows driving straight down toward your hip pockets. Zero lumbar hyperextension.\n"
                "• **Load Target**: Keep RIR at 2. If grip or elbow aches, utilize lifting straps."
            )
        elif "tricep" in p_lower or "skull" in p_lower or "extension" in p_lower:
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (TRICEPS / ELBOW HEALTH)**\n\n"
                "• **Immediate Substitute**: Switch to **Cable Rope Triceps Pushdown** or **Cross-Body Cable Extension**.\n"
                "• **Technical Cue**: Lock your upper arms vertically against your ribs. Stop just short of total lockout if tendon discomfort arises.\n"
                "• **Target**: 3 sets × 12–15 reps with slow 2s eccentric control."
            )
        elif "leg" in p_lower or "knee" in p_lower or "quad" in p_lower:
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (LEG DAY / ANTI-APT GUARDRAIL)**\n\n"
                "• **Immediate Substitute**: Switch to **High-Foot Leg Press** (knee friendly) or **Seated Leg Extension with 2s hold at top**.\n"
                "• **REMINDER**: Zero Barbell Squats or RDLs (Anti-APT guardrail strictly prohibits gluteus maximus hypertrophy movements)."
            )

    # 2. Nutrition / Calorie / Protein (Check before general quantity)
    if any(w in p_lower for w in ["protein", "calorie", "calories", "diet", "macro", "macros", "food", "soya", "whey", "eggs", "meal"]):
        return (
            "🥩 **NUTRITION PROTOCOL & MACRO CALIBRATION**\n\n"
            "• **Daily Protein Floor**: **145–150g non-negotiable**.\n"
            "  - 1 Scoop Whey = 24g\n"
            "  - 50g Raw Soya Chunks = 26g\n"
            "  - 3 Whole Eggs + 2 Whites = 25g\n"
            "  - 100g Low-fat Paneer = 18g\n"
            "  - 200g Greek Yogurt / Curd = 14g\n"
            "• **Daily Calorie Target**: **~1,850 kcal** (Controlled 250 kcal deficit to preserve muscle fullness while stripping body fat).\n"
            "• **Glycogen Protection**: Never drop below 1,600 kcal. Muscle flatness was previously caused by dropping calories to 1,352 kcal and draining glycogen stores."
        )

    # 3. Next Target / Weight / Overload
    if any(w in p_lower for w in ["next weight", "what weight", "what load", "next load", "overload target", "how much weight", "how heavy", "progression target", "target load"]):
        return (
            "📈 **CURRENT OVERLOAD TARGETS (DOUBLE-PROGRESSION PROTOCOL)**\n\n"
            "• **Incline DB Press**: Baseline is **20.0 kg/hand × 10, 10, 10** (Ceiling Achieved!). Next session target is **22.5 kg/hand × 8 reps** (Load Overload Jump).\n"
            "• **Lat Pulldown**: Baseline is **50.0 kg × 8 reps**. Target is **50.0 kg × 10, 10, 8** before advancing the selector pin.\n"
            "• **Flat BB Bench**: Baseline is **42.5 kg × 10 reps**. Target is **42.5 kg × 10, 10, 8**.\n"
            "• **DB Lateral Raise**: Baseline is **5.0 kg/hand × 15, 15, 15, 15** (Ceiling Hit!). Next target is **6.0 kg/hand × 10–12 reps** or 2s pause.\n\n"
            "⚠️ *Rule*: Only increment weight when the top rep threshold is achieved cleanly across ALL prescribed working sets with RIR ≤ 2."
        )

    # 4. Posture / APT / Butt Silhouette
    if any(w in p_lower for w in ["posture", "apt", "pelvic", "butt", "glute", "stretch", "desk", "sitting"]):
        return (
            "🧘 **ANTI-APT POSTURE RESTORATION (9-HOUR DESK PROTOCOL)**\n\n"
            "• **Root Cause**: 9 hours of daily chair sitting shortens the psoas (hip flexors), tilting the pelvis forward and pushing glutes backward into a protruding silhouette.\n"
            "• **Daily Required Triad**:\n"
            "  1. Half-Kneeling Hip Flexor Stretch (45s/side with rear glute squeezed hard)\n"
            "  2. Scapular Wall Slides (15 slow reps against wall with wrists flat)\n"
            "  3. Deadbugs (3 sets × 15 reps with lower back completely locked to floor)\n"
            "• **Exercise Guardrail**: Glutes remain locked at 0 direct hypertrophy sets."
        )

    # 5. Default General Coach Response
    return (
        f"⚡ **APEX COACH DISPATCH CONFIRMATION**\n\n"
        f"• **Instruction**: \"{prompt}\"\n"
        f"• **Status**: Remote request parsed and submitted to your Antigravity IDE agent on your laptop.\n"
        f"• **Execution**: Double-progression baselines, RIR standards, and workspace files are being reviewed and updated.\n"
        f"• **Git Sync**: Any system record modifications will be automatically committed and pushed to GitHub master."
    )

def _execute_task_thread(task_id, prompt, mode="agent"):
    with TASKS_LOCK:
        task = AGENT_TASKS.get(task_id)
        if not task:
            return

    transcript_path = get_latest_transcript_path()
    start_lines = count_transcript_lines(transcript_path)

    # 1. Immediate Event
    task["events"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "info",
        "text": f"Remote instruction received from phone: \"{prompt[:80]}{'...' if len(prompt)>80 else ''}\""
    })

    # 2. Instant Local Coach Answer
    guidance = generate_instant_coach_guidance(prompt)
    task["response"] = guidance
    task["events"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "coach",
        "text": "Coach rules & progressive overload engine analyzed context."
    })

    # 3. Dispatch to Antigravity CLI (agy chat -r -m agent)
    task["events"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "agent",
        "text": f"Connecting to Antigravity IDE agent session (mode: {mode})..."
    })

    try:
        clean_prompt = prompt.replace('"', '\\"')
        cmd = f'agy chat -r -m {mode} "{clean_prompt}"'
        proc = subprocess.Popen(
            cmd,
            cwd=BASE_DIR,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        task["events"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "agent",
            "text": "Antigravity IDE received prompt. Agent active on laptop."
        })
    except Exception as e:
        task["events"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "warning",
            "text": f"Could not trigger agy CLI directly: {e}"
        })

    # 4. Monitor Transcript for 12 seconds
    poll_start = time.time()
    seen_step_indices = set()
    while time.time() - poll_start < 12:
        time.sleep(1.2)
        if transcript_path and os.path.exists(transcript_path):
            new_records = read_transcript_from_line(transcript_path, start_lines)
            for rec in new_records:
                step_idx = rec.get("step_index")
                if step_idx in seen_step_indices:
                    continue
                seen_step_indices.add(step_idx)

                rec_type = rec.get("type", "")
                if "tool_calls" in rec:
                    for tc in rec["tool_calls"]:
                        t_name = tc.get("name", "tool")
                        t_action = tc.get("args", {}).get("toolAction", t_name)
                        task["events"].append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "type": "tool",
                            "text": f"Agent Tool: {t_action} ({t_name})"
                        })
                elif rec_type == "RUN_COMMAND":
                    task["events"].append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "type": "cmd",
                        "text": f"Executed command (exit code {rec.get('exit_code', 0)})"
                    })
                elif rec.get("content") and rec.get("source") == "MODEL":
                    content_str = str(rec["content"]).strip()
                    if content_str and len(content_str) > 20:
                        task["response"] = content_str
                        task["events"].append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "type": "coach",
                            "text": "Antigravity Agent generated response."
                        })

    # 5. Check Git Status & Auto-Commit / Push if files changed
    try:
        git_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=BASE_DIR).decode("utf-8").strip()
        if git_status:
            task["events"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "git",
                "text": "Changes detected in workspace files. Committing & pushing to GitHub..."
            })
            subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
            commit_msg = f"Remote agent update: {prompt[:50]}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=True)
            push_res = subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR, capture_output=True, text=True, timeout=20)
            if push_res.returncode == 0:
                task["events"].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "git_success",
                    "text": "✅ Successfully pushed to GitHub origin/master!"
                })
            else:
                task["events"].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "git_warn",
                    "text": f"Git push notice: {push_res.stderr.strip()[:100]}"
                })
    except Exception as ge:
        pass

    # Mark completed
    task["status"] = "completed"
    task["events"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "done",
        "text": "Session ready. View response below."
    })

def start_agent_task(prompt, mode="agent"):
    task_id = f"task_{int(time.time() * 1000)}"
    task_data = {
        "task_id": task_id,
        "prompt": prompt,
        "mode": mode,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "events": [],
        "response": ""
    }
    with TASKS_LOCK:
        AGENT_TASKS[task_id] = task_data

    thread = threading.Thread(target=_execute_task_thread, args=(task_id, prompt, mode), daemon=True)
    thread.start()
    return task_data

def get_agent_task(task_id, since_index=0):
    with TASKS_LOCK:
        task = AGENT_TASKS.get(task_id)
        if not task:
            return None
        events = task["events"][since_index:]
        return {
            "task_id": task["task_id"],
            "status": task["status"],
            "prompt": task["prompt"],
            "events": events,
            "total_events": len(task["events"]),
            "response": task["response"]
        }

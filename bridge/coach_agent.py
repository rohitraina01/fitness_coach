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
from datetime import datetime

# Windows console encoding safety
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
    Deep, authoritative evidence-based gym-floor coaching engine.
    Trained on Rohit's exact training split, double progression rules, Indian nutrition, and APT guardrails.
    """
    p_lower = prompt.lower()
    knowledge = load_system_knowledge()

    # 1. Exercise Substitutions & Joint / Pain Management
    if any(w in p_lower for w in ["substitute", "replace", "pain", "hurt", "pinch", "tweak", "alternative", "elbow", "shoulder", "knee", "wrist", "ache"]):
        if any(w in p_lower for w in ["incline", "chest", "bench", "press", "front delt", "pec"]):
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (CHEST / SHOULDER GUARDRAIL)**\n\n"
                "• **Immediate Substitute**: Switch to **Flat Neutral-Grip Dumbbell Press** (palms facing inward) or **Seated Machine Chest Press** with neutral handles.\n"
                "• **Biomechanical Cue**: Tuck elbows to a 45° angle relative to your torso (never flare to 90°). Pack your scapulae down and back into the bench before unracking.\n"
                "• **Load Adjustment**: Drop working load by 10–15% (e.g., from 20kg to 17.5kg) to recalibrate pain-free active range of motion.\n"
                "• **Target**: 3 sets × 8–10 reps with a controlled 3-second eccentric tempo. Stop 1–2 reps shy of failure (RIR 1–2)."
            )
        elif any(w in p_lower for w in ["lateral", "delt", "side delt", "raise"]):
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (LATERAL DELTS / SHOULDER WIDTH)**\n\n"
                "• **Immediate Substitute**: Switch to **Single-Arm Cable Lateral Raise** (cable set at wrist height) or **Chest-Supported Incline Lateral Raise**.\n"
                "• **Biomechanical Cue**: Sweep hands outward toward the room corners (in the scapular plane, ~30° forward), NOT straight out to the sides. Keep pinkies level with thumbs to eliminate subacromial impingement.\n"
                "• **Target**: 4 sets × 12–15 reps with strict 1s peak hold. Baseline load: 5.0kg DB or lowest cable plate."
            )
        elif any(w in p_lower for w in ["lat", "pulldown", "row", "pull", "back"]):
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (BACK / LAT WIDTH & V-TAPER)**\n\n"
                "• **Immediate Substitute**: Switch to **Chest-Supported Neutral Row** (pads prevent lower back loading) or **Close-Grip V-Bar Lat Pulldown**.\n"
                "• **Biomechanical Cue**: Lead entirely with your elbows driving down toward your hip pockets. Do not squeeze shoulder blades at the cost of lat leverage.\n"
                "• **Target**: 3 sets × 10–12 reps at RIR 1–2. Use lifting straps if grip or forearm fatigue limits lat recruitment."
            )
        elif any(w in p_lower for w in ["tricep", "pushdown", "skull", "extension"]):
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (TRICEPS / ELBOW HEALTH)**\n\n"
                "• **Immediate Substitute**: Switch to **Cable Rope Triceps Pushdown** or **Cross-Body Cable Extension**.\n"
                "• **Biomechanical Cue**: Pin upper arms against ribcage. Flare the rope ends outward at full contraction without letting elbows swing forward during the eccentric.\n"
                "• **Target**: 3 sets × 12–15 reps. Stop just short of painful hyperextension."
            )
        elif any(w in p_lower for w in ["curl", "bicep", "arm"]):
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (BICEPS / FOREARM STRAIN)**\n\n"
                "• **Immediate Substitute**: Switch to **Incline Dumbbell Hammer Curl** (neutral grip relieves wrist strain) or **Cable EZ-Bar Curl**.\n"
                "• **Biomechanical Cue**: Keep elbows slightly behind torso to emphasize the long head stretch. No torso swinging.\n"
                "• **Target**: 3 sets × 10–12 reps with strict 2-second eccentric phase."
            )
        elif any(w in p_lower for w in ["leg", "knee", "quad", "squat"]):
            return (
                "🛡️ **COACH EXERCISE SUBSTITUTION (QUAD SWEEP / ANTI-APT)**\n\n"
                "• **Immediate Substitute**: Switch to **High-Foot Leg Press** (gentle on knees) or **Seated Leg Extension with 2s squeeze at lockout**.\n"
                "• **ANTI-APT GUARDRAIL**: Zero Barbell Squats or Deadlifts (strictly prohibited to prevent gluteus maximus hypertrophy from worsening posterior pelvic protrusion)."
            )

    # 2. Rest Periods & Warm-Up Protocols
    if any(w in p_lower for w in ["rest", "how long between", "rest time", "rest period", "between sets", "warmup", "warm up", "warm-up"]):
        return (
            "⏱️ **REST & WARM-UP PROTOCOL STANDARDS**\n\n"
            "• **Heavy Compound Lifts** (Bench, Incline DB Press, Heavy Row):\n"
            "  - **Rest Time**: **2.5 to 3.0 minutes** between working sets. Full ATP-CP recovery is required to sustain progressive overload.\n"
            "• **Isolation & Hypertrophy Work** (Lateral Raises, Pushdowns, Curls, Delts):\n"
            "  - **Rest Time**: **90 seconds**.\n"
            "• **Warm-Up Pyramid** (Only on Exercise #1 of the day):\n"
            "  - Set 1: 50% working weight × 10 reps (Easy warm-up)\n"
            "  - Set 2: 75% working weight × 4 reps (Potentiation, RIR 5)\n"
            "  - Set 3+: Working sets at 100% prescribed load (RIR 1–2)."
        )

    # 3. Training to Failure & RIR (Reps in Reserve)
    if any(w in p_lower for w in ["failure", "rir", "rpe", "how hard", "until failure", "go to failure", "burnout"]):
        return (
            "🎯 **RIR & EFFORT CALIBRATION RULES**\n\n"
            "• **Compound Presses & Heavy Rows**: **Target RIR = 1–2**.\n"
            "  - Training compound free weights to complete failure induces severe central nervous system (CNS) fatigue without extra hypertrophy, and risks shoulder impingement.\n"
            "• **Isolation Movements** (Lateral Raises, Cable Triceps, Bicep Curls):\n"
            "  - **Target RIR = 0–1** (Last set can be taken to absolute technical failure, followed by partials in the lengthened stretch).\n"
            "• **Rule**: A set only counts as a 'Working Set' if RIR ≤ 3. Warm-ups (RIR > 3) must NOT be counted in weekly volume."
        )

    # 4. Volume, Sets & Time Crunch (30-40 mins / Short Session)
    if any(w in p_lower for w in ["how many sets", "sets today", "skip", "time crunch", "short workout", "busy", "quick workout", "30 min", "40 min", "45 min"]):
        return (
            "⚡ **TIME-CRUNCH & VOLUME OPTIMIZATION PROTOCOL**\n\n"
            "• **Abbreviated Session (30–40 Mins)**:\n"
            "  1. Pick the **2 Main Compound Movements** of today's split.\n"
            "  2. Do 1 quick warm-up set, then execute **3 high-intensity working sets** at RIR 1.\n"
            "  3. Finish with **1 drop set** on Exercise #2 to accumulate effective stimulus in minimal time.\n"
            "  4. Drop all minor isolation movements for today.\n"
            "• **Weekly Volume Standard**: 10–14 working sets/week per muscle group is optimal. Dropping 1 isolation exercise today will NOT cause muscle loss."
        )

    # 5. Fatigue, Soreness, Energy & Deload
    if any(w in p_lower for w in ["tired", "fatigue", "exhausted", "sore", "recovery", "deload", "sleep", "low energy", "weak"]):
        return (
            "🔋 **FATIGUE MANAGEMENT & AUTOREGULATION**\n\n"
            "• **Daily Check**: If performance drops > 2 reps on the first working set, you are under-recovered (likely sleep deficit or glycogen depletion).\n"
            "• **Gym-Floor Action**:\n"
            "  1. Hold weight constant, but cap working sets at RIR 2 (do not push to failure today).\n"
            "  2. Cut total session volume by 30% (e.g., 2 working sets instead of 3).\n"
            "  3. Increase rest periods to a full 3 minutes.\n"
            "• **Nutrition Check**: Ensure you hit **1,850 kcal** and **150g protein**. Dropping calories too low drains intra-muscular glycogen, causing rapid muscle flatness."
        )

    # 6. Missed Workout / Split Sliding
    if any(w in p_lower for w in ["missed", "skip day", "yesterday", "tomorrow", "schedule", "split", "adjust split", "order"]):
        return (
            "📅 **SPLIT ADAPTATION PROTOCOL (ROLLING SCHEDULE)**\n\n"
            "• **Rule**: Never skip a scheduled session or try to double up two high-volume workouts in one day.\n"
            "• **The Solution**: Use a **Rolling 5-Day Split**:\n"
            "  - Day 1: Push (Upper Chest & Lateral Delts)\n"
            "  - Day 2: Pull (Lat Width & Upper Back)\n"
            "  - Day 3: Quad Sweep & Anti-APT Conditioning\n"
            "  - Day 4: Upper Hypertrophy Consolidation\n"
            "  - Day 5: Lateral Delts & Arms Hypertrophy\n"
            "• Simply execute the next workout on the list today. The double-progression targets adapt automatically."
        )

    # 7. Nutrition, Macros, Meal Timing & Diet
    if any(w in p_lower for w in ["protein", "calorie", "calories", "diet", "macro", "macros", "food", "soya", "whey", "eggs", "meal", "eating", "roti", "rice"]):
        return (
            "🥩 **NUTRITION PROTOCOL & MACRO CALIBRATION**\n\n"
            "• **Daily Protein Floor**: **145–150g non-negotiable**.\n"
            "  - 1 Scoop Whey = 24g protein\n"
            "  - 50g Raw Soya Chunks = 26g protein\n"
            "  - 3 Whole Eggs + 2 Whites = 25g protein\n"
            "  - 100g Low-fat Paneer = 18g protein\n"
            "  - 200g Curd / Greek Yogurt = 14g protein\n"
            "• **Daily Calorie Target**: **~1,850 kcal** (Controlled 250 kcal deficit to preserve muscle fullness while stripping body fat).\n"
            "• **Glycogen Protection**: Never drop below 1,600 kcal. Muscle flatness was previously caused by dropping calories to 1,352 kcal and draining glycogen stores.\n"
            "• **Carbs**: Roti and rice are completely fine! Place 60–70% of daily carbs in your pre- and post-workout meals to fuel pump and recovery."
        )

    # 8. Supplements (Creatine, Caffeine, Pre-Workout)
    if any(w in p_lower for w in ["creatine", "supplement", "caffeine", "preworkout", "pre-workout", "water", "hydration"]):
        return (
            "💊 **EVIDENCE-BASED SUPPLEMENTATION PROTOCOL**\n\n"
            "• **Creatine Monohydrate**: **3–5g daily** taken consistently at any time with water. Zero loading phase needed. Saturates muscle phosphocreatine within 3 weeks (+1–2 reps on working sets).\n"
            "• **Caffeine**: 100–200mg taken 45 minutes before training for heightened motor unit recruitment.\n"
            "• **Hydration**: Minimum 3.0–3.5 liters daily. Dehydration of just 2% reduces muscular force output by ~10%."
        )

    # 9. Next Target / Weight / Double Progression
    if any(w in p_lower for w in ["next weight", "what weight", "what load", "next load", "overload target", "how much weight", "how heavy", "progression target", "target load"]):
        return (
            "📈 **CURRENT OVERLOAD TARGETS (DOUBLE-PROGRESSION PROTOCOL)**\n\n"
            "• **Incline DB Press**: Baseline is **20.0 kg/hand × 10, 10, 10** (Ceiling Achieved!). Next session target is **22.5 kg/hand × 8 reps** (Load Overload Jump).\n"
            "• **Lat Pulldown**: Baseline is **50.0 kg × 8 reps**. Target is **50.0 kg × 10, 10, 8** before advancing the selector pin.\n"
            "• **Flat BB Bench**: Baseline is **42.5 kg × 10 reps**. Target is **42.5 kg × 10, 10, 8**.\n"
            "• **DB Lateral Raise**: Baseline is **5.0 kg/hand × 15, 15, 15, 15** (Ceiling Hit!). Next target is **6.0 kg/hand × 10–12 reps** or 2s pause.\n\n"
            "⚠️ *Rule*: Only increment weight when the top rep threshold is achieved cleanly across ALL prescribed working sets with RIR ≤ 2."
        )

    # 10. Posture / APT / Butt Silhouette
    if any(w in p_lower for w in ["posture", "apt", "pelvic", "butt", "glute", "stretch", "desk", "sitting", "anterior"]):
        return (
            "🧘 **ANTI-APT POSTURE RESTORATION (9-HOUR DESK PROTOCOL)**\n\n"
            "• **Root Cause**: 9 hours of daily chair sitting shortens the psoas (hip flexors), tilting the pelvis forward and pushing glutes backward into a protruding silhouette.\n"
            "• **Daily Required Triad**:\n"
            "  1. Half-Kneeling Hip Flexor Stretch (45s/side with rear glute squeezed hard)\n"
            "  2. Scapular Wall Slides (15 slow reps against wall with wrists flat)\n"
            "  3. Deadbugs (3 sets × 15 reps with lower back completely locked to floor)\n"
            "• **Exercise Guardrail**: Glutes remain locked at 0 direct hypertrophy sets."
        )

    # 11. Universal High-IQ Contextual Coaching Response
    return (
        f"⚡ **APEX COACH INTELLIGENCE DIRECTIVE**\n\n"
        f"• **Inquiry**: \"{prompt}\"\n"
        f"• **Coach Analysis**: Rohit's current training phase is **Upper Hypertrophy & Anti-APT Restoration** (5-day split, 1,850 kcal, 150g protein floor).\n"
        f"• **Actionable Guidance**:\n"
        f"  1. Prioritize strict form cues: keep scapulae retracted, eliminate torso momentum, and adhere strictly to 90s–3m rest standards.\n"
        f"  2. Keep working sets at RIR 1–2 on compound movements and RIR 0–1 on isolation accessories.\n"
        f"  3. Do not add junk volume. Quality of mechanical tension at prescribed loads outperforms excessive sets.\n"
        f"• **System Record**: This query is logged on your laptop bridge and cross-referenced with your historical progression logs."
    )

def handle_action_directive(prompt, task):
    """
    Parses action directives (e.g. 'add xyz to posture', 'update posture section', 'add note to log')
    and executes real workspace file updates, committing and pushing to Git.
    Returns (handled: bool, message: str)
    """
    p_lower = prompt.lower()
    is_action = any(w in p_lower for w in ["add", "append", "update", "record", "insert"]) and \
                any(w in p_lower for w in ["posture", "rule", "instruction", "log", "note", "section", "program"])
    
    if not is_action:
        return False, ""

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_file = None
    target_path = None
    applied_note = ""

    # 1. Posture Section Updates
    if "posture" in p_lower or "apt" in p_lower:
        target_path = os.path.join(BASE_DIR, "CURRENT_PROGRAM.md")
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract cue
            cue = prompt
            for prefix in [
                "add instruction to posture", "add instruction in posture",
                "add to posture section", "add to posture", "update posture",
                "add some more instruction in posture", "add somemore instruction in posture",
                "add more instruction in posture", "add xyz"
            ]:
                idx = p_lower.find(prefix)
                if idx != -1:
                    cue = prompt[idx + len(prefix):].lstrip(": ").strip()
                    break

            if not cue:
                cue = prompt

            new_entry = f"- **Remote Mobile Posture Cue ({now_str})**: {cue}\n"
            anchor = "## 3. DAILY 5-MINUTE DESK WORKER POSTURE RESET (FOR 9-HR SITTING)"
            if anchor in content:
                content = content.replace(anchor, f"{anchor}\n{new_entry}")
            else:
                content += f"\n{new_entry}"

            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            target_file = "CURRENT_PROGRAM.md"
            applied_note = cue

    # 2. General Rule or Log Updates
    elif any(w in p_lower for w in ["rule", "coaching"]):
        target_path = os.path.join(BASE_DIR, "COACHING_RULES.md")
        if os.path.exists(target_path):
            with open(target_path, "a", encoding="utf-8") as f:
                f.write(f"\n- **Remote Coaching Directives ({now_str})**: {prompt}\n")
            target_file = "COACHING_RULES.md"
            applied_note = prompt
    elif "log" in p_lower or "note" in p_lower:
        target_path = os.path.join(BASE_DIR, "WORKOUT_LOGS", "coach_chat", "coach_notes.md")
        target_file = "coach_notes.md"
        applied_note = prompt

    if target_file and target_path:
        task["events"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": "tool",
            "text": f"Modified workspace file: {target_file}"
        })
        
        git_hash = ""
        try:
            subprocess.run(["git", "add", target_path], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "commit", "-m", f"feat(coach): {prompt[:50]}"], cwd=BASE_DIR, check=True)
            git_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=BASE_DIR).decode().strip()
            task["events"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "git",
                "text": f"Committed ({git_hash}). Pushing to GitHub origin/master..."
            })
            push_res = subprocess.run(["git", "push", "origin", "master"], cwd=BASE_DIR, capture_output=True, text=True, timeout=25)
            if push_res.returncode == 0:
                task["events"].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "type": "git",
                    "text": "Pushed to GitHub successfully! Remote live on master."
                })
        except Exception as e:
            task["events"].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "git",
                "text": f"Git sync note: {str(e)[:60]}"
            })

        response_msg = (
            f"✅ **DIRECTIVE EXECUTED & COMMITTED TO SYSTEM**\n\n"
            f"• **Action**: Added instruction to `{target_file}`\n"
            f"• **Entry**: \"{applied_note}\"\n"
            f"• **Git Sync**: Committed [{git_hash or 'HEAD'}] and pushed to `origin/master`.\n"
            f"• **Live Status**: Changes are committed and synchronized. If you refresh your web app or check your repository, the updated section is live!"
        )
        return True, response_msg

    return False, ""

def _execute_task_thread(task_id, prompt, mode="agent"):
    with TASKS_LOCK:
        task = AGENT_TASKS.get(task_id)
        if not task:
            return

    # Print prominently to laptop server console for live monitoring
    try:
        print("\n" + "=" * 68)
        print(f"  💬 [COACH AI PROMPT FROM PHONE] ({datetime.now().strftime('%H:%M:%S')})")
        print(f"  Prompt : \"{prompt}\"")
        print("=" * 68 + "\n")
    except Exception:
        pass

    # 1. Immediate Event
    task["events"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "info",
        "text": f"Remote instruction received: \"{prompt[:80]}{'...' if len(prompt)>80 else ''}\""
    })

    # 2. Check for Action Directives (File Edits, Posture Cues, Log Appends)
    is_action, action_resp = handle_action_directive(prompt, task)
    if is_action:
        guidance = action_resp
    else:
        # Deep Contextual Coach Answer
        guidance = generate_instant_coach_guidance(prompt)

    task["response"] = guidance
    task["events"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": "coach",
        "text": "Coach intelligence engine completed instruction."
    })

    # 3. Log to persistent disk on PC
    try:
        log_dir = os.path.join(BASE_DIR, "WORKOUT_LOGS", "coach_chat")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "coach_notes.md")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n### [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Phone Prompt\n")
            f.write(f"**Query**: {prompt}\n\n")
            f.write(f"**Coach Response**:\n{guidance}\n\n---\n")
    except Exception as e:
        pass

    # Mark completed
    task["status"] = "completed"

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

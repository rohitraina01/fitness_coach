# APEX FITNESS COACH: COMPLETE OPERATING & AUTOMATION MANUAL

> **Autonomous Evidence-Based Fitness System with Remote Mobile Bridge & Antigravity Agent Orchestration**

---

## 1. QUICK COMMAND CENTER (`commands/`)

All system operations and automation scripts are located in the [`commands/`](file:///d:/Workspace/fitness_coach/commands/) folder. For your convenience, root shortcuts are also maintained.

| Script | Location | Purpose & Behavior |
| :--- | :--- | :--- |
| **`start_server.bat`** | [`commands/start_server.bat`](file:///d:/Workspace/fitness_coach/commands/start_server.bat) | Starts the bridge server on port `8080`. Displays your local network IP for phone access. **Closing this terminal window terminates the server automatically.** |
| **`kill_server.bat`** | [`commands/kill_server.bat`](file:///d:/Workspace/fitness_coach/commands/kill_server.bat) | Finds any active process listening on port `8080` (or recorded in `.server.pid`) and forcefully terminates it cleanly. |
| **`open_coach_session.bat`** | [`commands/open_coach_session.bat`](file:///d:/Workspace/fitness_coach/commands/open_coach_session.bat) | Pulls latest workouts from GitHub, then launches an autonomous coaching chat session directly inside Antigravity IDE (`agy chat -r -m agent`). |
| **`push_to_github.bat`** | [`commands/push_to_github.bat`](file:///d:/Workspace/fitness_coach/commands/push_to_github.bat) | Stages all workspace modifications, generates an auto-commit, and pushes to remote GitHub (`origin/master`). |
| **`pull_from_github.bat`** | [`commands/pull_from_github.bat`](file:///d:/Workspace/fitness_coach/commands/pull_from_github.bat) | Pulls and fast-forwards your local workspace with any workouts logged via cloud runners or external devices. |
| **`rebuild_dashboard.bat`** | [`commands/rebuild_dashboard.bat`](file:///d:/Workspace/fitness_coach/commands/rebuild_dashboard.bat) | Refreshes the dynamic Excel analytics workbook ([`fitness_dashboard.xlsx`](file:///d:/Workspace/fitness_coach/DASHBOARD/fitness_dashboard.xlsx)) and regenerates phone HTML cards. |
| **`run_integrity_audit.bat`** | [`commands/run_integrity_audit.bat`](file:///d:/Workspace/fitness_coach/commands/run_integrity_audit.bat) | Executes [`scripts/audit_integrity.py`](file:///d:/Workspace/fitness_coach/scripts/audit_integrity.py) to audit primary keys, foreign keys, and unit bounds. |

---

## 2. SERVER LIFECYCLE & SHUTDOWN

### Starting the Server
- Double-click [`commands/start_server.bat`](file:///d:/Workspace/fitness_coach/commands/start_server.bat) (or run [`start_server.bat`](file:///d:/Workspace/fitness_coach/start_server.bat) from root).
- The window title will display: `Apex Coach Bridge Server (Port 8080)`.
- The terminal detects and prints your PC's local Wi-Fi IPv4 address (e.g., `192.168.1.45`).
- The server saves its Process ID to `bridge/.server.pid`.

### Stopping the Server (Two Methods)
1. **Window Close (Simplest & Most Practical)**: Simply click the `X` button on the terminal window. Because the Python process is bound to the console, the bridge server terminates immediately.
2. **From Command / Remote Window**: Double-click [`commands/kill_server.bat`](file:///d:/Workspace/fitness_coach/commands/kill_server.bat). It instantly checks port `8080`, terminates the process, and cleans up the PID file.

---

## 3. ACCESSING FROM YOUR PHONE ON THE GYM FLOOR

### Method A: Same Home Wi-Fi
1. Launch `commands/start_server.bat`. Note your IPv4 address (e.g. `192.168.1.45`).
2. Open your phone browser and go to:
   ```
   http://192.168.1.45:8080
   ```
3. Tap **Share ➔ Add to Home Screen** (iOS) or **Install / Add to Home screen** (Android) to run it like a native full-screen app.

### Method B: Anywhere in the World via Tailscale (Recommended)
1. Install [Tailscale](https://tailscale.com) on your PC and Phone (100% free private mesh VPN).
2. Sign in to both devices with the same account.
3. Open `http://<YOUR-PC-TAILSCALE-IP>:8080` in your phone browser.
4. **Result**: Seamless encrypted connection 24/7 over cellular data at any gym.

### Method C: Cloudflare Tunnel (Zero-Config HTTPS)
1. Run this command in a terminal:
   ```bash
   cloudflared tunnel --url http://localhost:8080
   ```
2. Cloudflare generates a public secure URL (e.g. `https://xxxx.trycloudflare.com`). Bookmark that on your phone!

---

## 4. GYM WORKOUT LOGGING WORKFLOW

When your workout is complete (or set-by-set):
1. On your phone, tap the **📝 Log** tab.
2. Select your session type (**Pull**, **Push**, **Legs**).
3. Type or tap **🎙️ Dictate** to speak your sets (e.g., `"Lat pulldown 50kg x 10, 10, 8. Cable curls 20kg x 12, 10"`).
4. Tap **Process Workout ➔**:
   - The phone sends the log to the PC bridge server.
   - The server triggers [`scripts/ingest_workout.py`](file:///d:/Workspace/fitness_coach/scripts/ingest_workout.py).
   - Records are normalized and appended to [`DATA/workouts.csv`](file:///d:/Workspace/fitness_coach/DATA/workouts.csv) & [`DATA/workout_sets.csv`](file:///d:/Workspace/fitness_coach/DATA/workout_sets.csv).
   - Dated Markdown log is created in [`WORKOUT_LOGS/`](file:///d:/Workspace/fitness_coach/WORKOUT_LOGS/).
   - Excel Dashboard is refreshed.
   - **Automated Git Push**: The server stages all files, commits, and automatically pushes to GitHub `origin/master`.
   - **Dynamic In-App Update**: The phone UI automatically refreshes the workout floor and progress graphs in place without requiring a page reload!

---

## 5. REMOTE COACH AI & LIVE AGENT STREAMING

You can talk to your laptop's AI coach directly from your phone while resting between sets at the gym!

### How It Works
1. Tap the **🤖 Coach AI** tab in the phone app.
2. Tap a quick chip (e.g., `🛡️ Shoulder Fix`, `📈 Next Overload`, `🥩 Macro Protocol`) OR type / dictate any custom question or instruction:
   - *"My left shoulder is pinching on Incline DB Press. What is an evidence-based substitute?"*
   - *"I hit 22.5kg for 8, 8, 8 today. Advance my double progression target."*
   - *"Change Day 3 arm volume to 10 sets in CURRENT_PROGRAM.md and push to git."*
3. Tap **Send to Laptop ➔**:
   - **Instant Coach Guidance**: For urgent gym-floor questions, an instant evidence-based coach response appears in ~1 second.
   - **Laptop Agent Dispatch**: The server invokes `agy chat -r -m agent` to engage Antigravity IDE on your laptop.
   - **Live Activity Stream**: You see the laptop agent's real-time events on your phone:
     - `[18:15:02] Remote instruction received`
     - `[18:15:04] Tool executed: replace_file_content CURRENT_PROGRAM.md`
     - `[18:15:06] Git push completed: origin/master`
   - **Auto-Commit & Auto-Deploy**: Any files updated by the agent on your PC are automatically committed and pushed to GitHub!

---

## 6. SMART OFFLINE QUEUE (WHEN PC IS TURNED OFF)

If your laptop is turned off or you have zero internet in the gym:

1. **Zero Data Loss**: Both **Workout Logs** and **Coach Prompts** are automatically saved into your phone's encrypted browser storage (`localStorage`).
2. **Queue Drawer**: View pending items under the **Pending Offline Queue** section.
3. **Synchronization**:
   - When you turn your PC on, tap **Sync to PC ➔** (or **Dispatch to Laptop ➔**) to process the queued items.
   - If you already logged the workout manually at home, tap **Discard / Delete** to prevent accidental duplicate database entries!
4. **Cloud Runner Fallback**: If you configure your GitHub PAT token in **⚙️ Settings**, workouts can also dispatch directly to GitHub Cloud Actions even when your PC is off!

---

## 7. SYSTEM CREDENTIALS & SECURITY

- **Default App Security PIN**: `123` (Change to your secret 4-digit PIN in the **⚙️ Settings** modal).
- **Lock App**: Tap the **🔒** icon in the header to instantly lock your workout records from prying eyes.

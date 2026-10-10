# APEX COACH MOBILE BRIDGE

A lightweight, zero-dependency mobile web application and local bridge server that enables you to control your fitness coaching system directly from your phone while you are at the gym.

---

## 1. HOW IT WORKS
1. **Phone Web App (`bridge/web/`)**: Opens directly in any mobile browser (Safari, Chrome, etc.). Can be saved to your phone's home screen as a Progressive Web App (PWA).
2. **Local Bridge Server (`bridge/server.py`)**: Runs on port 8080 on your PC. It receives incoming workout logs from your phone, executes the system's 7-stage workflow using `scripts/ingest_workout.py`, updates CSV databases, regenerates `fitness_dashboard.xlsx`, and commits changes to Git.
3. **Smart Offline Queue**:
   - If your PC is **online**: The workout is processed and committed immediately.
   - If your PC is **offline**: The workout is saved into your phone's secure local queue.
   - You can tap **Sync to PC** when your PC boots up, OR tap **Discard / Delete** if you already logged the workout manually on your PC (guaranteeing zero accidental duplicate entries!).

---

## 2. HOW TO ACCESS FROM YOUR PHONE

### Method A: Same Home Wi-Fi (Simplest)
1. Double-click `bridge/start_bridge.bat` (or run `python bridge/server.py`).
2. The terminal will display your local IPv4 address (e.g., `192.168.1.45`).
3. On your phone connected to the same Wi-Fi, open your browser and go to:
   ```
   http://192.168.1.45:8080
   ```
4. Tap **Share ➔ Add to Home Screen** on iPhone or **Install / Add to Home screen** on Android.

---

### Method B: Access Anywhere Outside Home (Gym Floor via Cloudflare Tunnel)
To access from cellular data at the gym without port forwarding or exposing your IP:
1. Download [cloudflared](https://github.com/cloudflare/cloudflared/releases) (or install via `winget install Cloudflare.cloudflared`).
2. Run this free temporary tunnel command:
   ```bash
   cloudflared tunnel --url http://localhost:8080
   ```
3. Cloudflare gives you a free secure HTTPS URL (e.g., `https://your-unique-link.trycloudflare.com`).
4. Bookmark that link on your phone. You can now log workouts and view your live dashboard from any gym or cellular network in the world!

---

### Method C: Access via Tailscale (Zero-Trust Private Mesh)
1. Install [Tailscale](https://tailscale.com) on your PC and on your Phone (100% free for personal use).
2. Sign in on both devices.
3. Open `http://<your-pc-tailscale-ip>:8080` on your phone browser. It works anywhere 24/7 over encrypted private wireguard.

---

## 3. FEATURES AT A GLANCE
- **Today's Workout Floor**: Live exercise order, set checklists with local state persistence, rest countdown timer with buzzer and vibration.
- **Quick Log & Voice Dictation**: Type or use your phone microphone to dictate sets.
- **Smart Queue**: Pending workouts show up with both **Sync** and **Discard / Delete** buttons.
- **9-Hour Desk Posture Hub**: Interactive timers for Anti-APT stretches, scapular wall slides, and lower-abs bracing.
- **Progress Analytics**: Native canvas graphs showing your 30-day weight trajectory (with rolling average) and protein consistency against your 150g floor.

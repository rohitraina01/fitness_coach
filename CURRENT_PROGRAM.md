# DYNAMIC TRAINING ARCHITECTURE: REAL-TIME HYPERTROPHY & ANTI-APT ENGINE

*Version: 4.0 (Zero-Static-Template Dynamic Synthesis)*  
*Active Since: 2026-11-28*  
*Core Philosophy: Workouts are NEVER copied from a static weekly template. Every next session (`CURRENT_NEXT_WORKOUT.md`) is synthesized fresh in real time from `DATA/workouts.csv`, `DATA/workout_sets.csv`, `COACH_MEMORY.md`, recovery days elapsed, and exercise science.*

---

## 1. DYNAMIC DECISION ENGINE (HOW EVERY NEXT WORKOUT IS BUILT)

Before prescribing `CURRENT_NEXT_WORKOUT.md`, the coach executes `python scripts/coach_brief_context.py` and evaluates 4 live inputs:
1. **Systemic & Muscular Freshness (`COACH_MEMORY.md` + Days Elapsed)**:
   - Which muscle groups have rested $\ge$ 48–72 hours (or > 7–14 days)?
   - Was there external lower-body or systemic stress (e.g., cricket, trekking, poor sleep, high work stress)?
2. **Rule 9 Anti-Leg-Skipping Gate**:
   - Maximum **2 consecutive upper-body sessions (Push or Pull)** before **Legs & Core** is mandatory.
   - Outside that hard lock, session type (`Push`, `Pull`, `Legs & Core`) is autoregulated to target the freshest, highest-priority musculature.
3. **Real-Time CSV Telemetry (`DATA/workout_sets.csv`)**:
   - **Cleared Rep Ceiling**: Advance load by the smallest real gym increment (e.g., +2.5 kg DB, +5 kg cable stack) OR expand rep target.
   - **Layoff > 14 Days**: Include a mandatory submaximal feeler set (e.g., 17.5 kg × 4 before 22.5 kg Incline DB) and cap RIR at 1–2 on compounds.
   - **Fatigue / Rep Collapse**: Diagnose whether exercise ordering caused local metabolic fatigue (e.g., back-to-back pressing/rowing) and reorder or swap to a higher-stability angle.
4. **Tier-1 Aesthetic Priority Allocation (`GOALS.md`)**:
   - **Lateral Delts (Tier 1 — 12–16 sets/wk)**: Must be hit from **both** lengthened (Cable) and shortened (DB) profiles on Push days when training frequency is < 4–5x/week.
   - **Lats & Upper Back (Tier 1 — 12–16 sets/wk)**: Vertical pull + horizontal row with wrist straps mandatory; Rear Delts placed *before* heavy rows to prevent post-row shoulder burn.
   - **Arms — Biceps & Triceps (Tier 1 — 12–14 sets/wk)**: Prioritize stretch-mediated growth (**Overhead Cable Triceps Extension** for long head; **EZ-Bar + Hammer Curl** for peak/brachialis).
   - **Upper Chest (Tier 1 — 10–12 sets/wk)**: 30° Incline DB Press anchor; avoid flat-press overlap unless sternal chest is lagging or rested > 14 days.
   - **Anti-APT Core & Hamstrings (Tier 2 — 8–10 sets/wk)**: Dorsiflexed Leg Curls + Lumbar-Glued Floor Crunch & Deadbug + Hip Flexor Stretch. **0% glutes**.

---

## 2. SCIENTIFIC SEQUENCING & SESSION GUARDRAILS (RULES 9 & 10)

- **Rule 10 — Zero Back-to-Back Same-Muscle Stacking**:
  - Never place two exercises targeting the same primary muscle group consecutively (`Chest → Chest`, `Back → Back`, `Quads → Quads`, `Biceps → Biceps`, `Triceps → Triceps`).
  - Always interleave a non-competing muscle between them (e.g., `Incline DB → Cable Lateral → Smith Bench → Overhead Triceps → DB Lateral → Pec Deck`, or `Pulldown → Rear Delt Fly → Seated Row → EZ Curl → DB Row → Hammer Curl`, or `Leg Press → Leg Curl → Leg Extension`).
- **Session Density Cap**: **14–17 working sets max**, completed in **50–55 minutes**.
- **RIR Standards**: **1–2 RIR** on multi-joint compounds; **0–1 RIR** on stable machines and isolations.

---

## 3. APPROVED EQUIPMENT-VERIFIED EXERCISE POOL

The coach dynamically selects and orders 5–6 movements per session from this verified catalog (never prescribing banned movements or missing equipment):

| Movement Slot | Approved Exercises | Verified Gym Equipment Constraints |
| :--- | :--- | :--- |
| **Upper Chest** | `INCLINE_DB_PRESS` (30°), `INCLINE_MACHINE_PRESS` | DBs: 1,2,3,4,5,7,8, 10, 12.5, 15, 17.5, 20, 22.5 kg |
| **Sternal / Mid Chest** | `SMITH_BENCH`, `FLAT_BB_BENCH`, `PEC_DECK_FLY` | Pec Deck +5 kg increments above 10 kg |
| **Lateral Delts** | `CABLE_LATERAL_RAISE` (lengthened), `DB_LATERAL_RAISE` (shortened) | **NO 6.0 kg DB** (5 → 7 kg is +40%; build reps to 15–20 @ 5 kg or use 2.5 kg cables) |
| **Triceps** | `OVERHEAD_TRICEPS_EXT` (long-head stretch priority), `TRICEPS_PUSHDOWN`, `ROPE_PUSHDOWN` | +5 kg jumps on stacks (master 12–15 reps before jumping pin) |
| **Vertical Pull (Lats)** | `PULL_UP`, `LAT_PULLDOWN` (Neutral/Close), `SINGLE_ARM_LAT_PULLDOWN`, `STRAIGHT_ARM_PULLDOWN` | Lifting wrist straps mandatory |
| **Horizontal Pull (Back)** | `SEATED_CABLE_ROW` (V-Bar, elbows 30–45°), `DB_SINGLE_ARM_ROW` (bench-braced) | **NO unstable standing/unsupported cable rows** |
| **Rear Delts** | `REAR_DELT_FLY` (Reverse Pec Deck), `FACE_PULL` | Train *before* heavy rows to avoid rear/side delt burn |
| **Biceps / Brachialis** | `EZ_BAR_CURL`, `HAMMER_CURL`, `CABLE_CURL`, `INCLINE_DB_CURL` | 5.0 / 7.5 kg DBs for Hammer Curls |
| **Quads (0% Glute)** | `LEG_PRESS` (narrow/mid-low stance), `LEG_EXTENSION` | **ZERO Squats, Deadlifts, Hip Thrusts, Lunges** |
| **Hamstrings** | `LEG_CURL` (Lying/Seated, toes strictly dorsiflexed) | Shuts off calves to isolate hamstrings |
| **Calves** | `BW_CALF_RAISE` (elevated step / single-leg / DB-loaded) | **NO Standing Calf Raise Machine in gym** |
| **Anti-APT Core & Posture** | `FLOOR_CRUNCH`, `DEADBUG`, `LYING_LEG_RAISE`, `Half-Kneeling Hip Flexor Stretch` | Stretches prescribed in **hold seconds** (`4 total holds: 2/leg × 30–45s`), never reps |

---

## 4. DAILY 5-MINUTE DESK WORKER POSTURE RESET (FOR 9-HR SITTING)
- **Half-Kneeling Hip Flexor Stretch**: 2 sets × 45s per side (squeeze rear glute, posterior pelvic tilt).
- **Scapular Wall Slides**: 15 slow reps against wall (wrists & elbows flat).
- **Suboccipital Release & Wall Chin Tucks**: 60s skull-base release + 15 × 3s chin retractions.

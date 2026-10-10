# PERSONAL FITNESS COACHING & PROGRESSION SYSTEM

An autonomous, evidence-based training, nutrition, and data tracking environment built to persist across model changes, conversation resets, and multi-year physique progression.

---

## 1. QUICKSTART & DAILY USE

### The Simplest Way to Use the System After Every Gym Session
After finishing your workout, open the chat and paste your raw workout notes. For example:
> "Just finished Pull: Lat Pulldown 55kg x 10, 10, 9 (1 RIR); Chest supported row 40kg x 10, 10, 8; Straight arm pulldown 25kg x 14, 13; Rear delt fly 35kg x 15, 14; Cable curls 20kg x 11, 10; Hammer curls 12kg x 10, 9. Felt great, 55 mins."

The system automatically executes the **7-Stage Workflow**:
1. **Ingests** and maps your lifts to canonical IDs.
2. **Retrieves** previous performance baselines from `DATA/workout_sets.csv`.
3. **Analyzes** progressive overload under double-progression rules.
4. **Coaches** with strict, objective feedback (no participation trophies).
5. **Persists** the dated Markdown log in `WORKOUT_LOGS/YYYY/YYYY-MM/` and appends normalized rows to `DATA/workouts.csv` and `DATA/workout_sets.csv`.
6. **Refreshes** the Excel analytics dashboard (`DASHBOARD/fitness_dashboard.xlsx`) and phone workout exports (`OUTPUTS/mobile/`).
7. **Reports** your performance review and generates your exact next workout prescription.

---

## 2. REPOSITORY ARCHITECTURE

```
fitness_coach/
├── AGENTS.md                   # Core repository instructions & operating guidelines
├── README.md                   # This user manual, recovery, and architecture guide
├── MASTER_COACH_PROMPT.md      # Coach persona, hypertrophy axioms, review protocol
├── PROFILE.md                  # Trainee profile, equipment constraints, diet baseline
├── GOALS.md                    # Target physique attributes, priority tiers, phased plan
├── COACHING_RULES.md           # Double progression rules, RIR standards, deload triggers
├── NUTRITION_RULES.md          # Calorie deficit targets, Indian meal plans, protein guide
├── DATA_DICTIONARY.md          # Full schemas, validation constraints, foreign keys
├── CHANGELOG.md                # System modifications and historical event log
├── CURRENT_PROGRAM.md          # Active 5-day aesthetic hypertrophy split
├── CURRENT_NEXT_WORKOUT.md     # Immediate next session targets (phone-ready markdown)
├── CURRENT_STATUS.md           # Compact system snapshot for rapid AI retrieval
├── EXERCISE_CATALOG.md         # Narrative catalog with form cues and biomechanics
├── WORKOUT_LOGS/               # Chronological markdown workout logs
│   └── 2026/
│       ├── 2026-09/            # September logs (2026-09-21, 24, 25, 28)
│       └── 2026-10/            # October logs (2026-10-01, 04, 10)
├── NUTRITION_LOGS/             # Monthly nutrition summaries
├── BODY_METRICS/               # Weigh-ins and body tape measurements
│   ├── weigh_ins.csv
│   └── body_measurements.csv
├── DATA/                       # Core relational database (CSV)
│   ├── workouts.csv            # 1 row per workout
│   ├── workout_sets.csv        # 1 row per set
│   ├── exercise_catalog.csv    # Canonical exercises & biomechanics
│   ├── body_metrics.csv        # Fasted morning weights & rolling averages
│   ├── nutrition.csv           # Calories, macros, steps, water
│   └── adherence.csv           # Weekly training consistency
├── DASHBOARD/                  # Excel visualizer & analytics workbook
│   ├── fitness_dashboard.xlsx  # Multi-sheet workbook with Excel tables & charts
│   └── dashboard_README.md     # Dashboard usage and architecture guide
├── SKILLS/                     # Native skills (ingestion, analysis, planning, audits)
├── .agents/skills/             # Antigravity IDE native skill mirror
├── scripts/                    # Automation scripts
│   ├── ingest_workout.py       # Autonomous workout ingestion engine
│   ├── build_dashboard.py      # Automated openpyxl Excel dashboard builder
│   ├── audit_integrity.py      # Relational & referential data integrity auditor
│   └── export_mobile.py        # Generates phone clipboard TXT & mobile HTML cards
├── tests/                      # Automated Python test suite
└── OUTPUTS/                    # Generated review documents & mobile files
    ├── mobile/                 # next_workout.txt & next_workout.html
    ├── weekly-reviews/         # Weekly progress assessments
    ├── monthly-reviews/        # Mesocycle review reports
    └── archived-plans/         # Superseded training programs
```

---

## 3. EXCEL DASHBOARD CAPABILITIES
The file `DASHBOARD/fitness_dashboard.xlsx` features:
- **Executive Dashboard**: KPI summary cards for scale weight, calorie deficit, daily protein, training adherence %, and immediate next workout.
- **Relational Tables**: `Table_Workouts`, `Table_WorkoutSets`, `Table_ExerciseCatalog`, `Table_BodyMetrics`, `Table_Nutrition`, `Table_VolumeAttribution`, and `Table_Adherence`.
- **Native Excel Charts**:
  - *Body Weight Trend Chart*: Dynamically tracks scale weight against dates.
  - *Weekly Hypertrophy Volume Chart*: Compares planned vs actual sets per target muscle.
  - *Training Adherence Chart*: Tracks week-over-week attendance consistency.
- **Auto-Expansion**: Generated programmatically using Python and `openpyxl`. Run `python scripts/build_dashboard.py` at any time to regenerate the workbook from source CSVs.

---

## 4. GYM FLOOR MOBILE ACCESS
Before leaving for the gym:
- Open `OUTPUTS/mobile/next_workout.html` in your browser on your phone (or view `OUTPUTS/mobile/next_workout.txt`).
- Features: Clean dark-mode interface, exercise ordering, set-by-set targets (floor, main, stretch), rest times, form cues, and interactive set checkboxes.

---

## 5. CLI AUTOMATION COMMANDS

### Ingesting a Workout via CLI
```bash
python scripts/ingest_workout.py --type "Pull" --name "Pull A" --duration 55 --notes "Felt strong" --json-sets '[{"exercise": "LAT_PULLDOWN", "load": 55, "reps": 10, "rir": 1}, {"exercise": "CHEST_SUPPORTED_ROW", "load": 40, "reps": 10, "rir": 1}]'
```

### Auditing Data Integrity
```bash
python scripts/audit_integrity.py
```

### Rebuilding Excel Dashboard
```bash
python scripts/build_dashboard.py
```

### Updating Mobile Exports
```bash
python scripts/export_mobile.py
```

### Running Test Suite
```bash
python -m unittest discover -s tests -v
```

---

## 6. BACKUPS, SYNCING & SYSTEM RECOVERY
- **Portability**: All data is stored in open, text-based formats (Markdown and CSV) plus standard OpenXML XLSX. No external database server or cloud subscription is required.
- **Git Versioning**: The entire workspace is tracked with Git:
  ```bash
  git add .
  git commit -m "Log workout W-YYYYMMDD-01"
  ```
- **Sync Across Devices**: The repository can be synced via Git (GitHub/GitLab private repo) or Google Drive / OneDrive.
- **Switching Between Codex & Antigravity**:
  - Codex uses `AGENTS.md` located at root.
  - Antigravity uses `.agents/skills/` and workspace prompt mechanisms.
  - Both environments share identical data tables, scripts, and documentation.

---

## 7. CURRENT LIMITATIONS & TODO LIST
1. **Historical Set Backfill**: The 7 historical sessions between 2026-09-21 and 2026-10-10 are indexed with dates and exercises, but exact loads and reps were not captured in prior logs. Backfill any known weights into `DATA/workout_sets.csv` if available.
2. **Lower Body Absence**: Zero leg training sessions were recorded in recent weeks. Leg day (Day 3 in `CURRENT_PROGRAM.md`) must be initiated to prevent muscular imbalance.
3. **Daily Fasted Weigh-Ins**: Record morning weight in `BODY_METRICS/weigh_ins.csv` to establish true 7-day rolling averages and calibrate maintenance calories.
4. **Tape Measurements**: Record baseline waist (navel), chest, shoulder, and arm circumferences in `BODY_METRICS/body_measurements.csv`.

# DATA DICTIONARY & SCHEMA SPECIFICATION

This document details the relational schemas, column constraints, units, and validation rules for all structured data tables in `DATA/` and `BODY_METRICS/`.

---

## 1. `DATA/workouts.csv`
Records high-level session metadata. One row per workout.

| Column | Type | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `workout_id` | String | NO | Primary Key. Format: `W-YYYYMMDD-NN` | `W-20261010-01` |
| `date` | Date | NO | ISO 8601 Date: `YYYY-MM-DD` | `2026-10-10` |
| `session_type` | String | NO | Category: `Push`, `Pull`, `Legs`, `Upper`, `Lower`, `Rest` | `Push` |
| `session_name` | String | NO | Specific split day title | `Push A` |
| `duration_min` | Integer| YES | Total workout duration in minutes | `65` |
| `readiness_score`| Integer| YES | Subjective pre-workout readiness (1–10) | `8` |
| `status` | String | NO | `COMPLETED`, `PARTIAL`, `INCOMPLETE_HISTORICAL`, `SKIPPED` | `INCOMPLETE_HISTORICAL` |
| `notes` | String | YES | General workout notes, subjective feeling | `High fatigue` |

---

## 2. `DATA/workout_sets.csv`
Records every individual set performed. One row per set.

| Column | Type | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `set_id` | String | NO | Primary Key. Format: `S-YYYYMMDD-NN-MM` | `S-20261010-01-01` |
| `workout_id` | String | NO | Foreign Key $\rightarrow$ `workouts.workout_id` | `W-20261010-01` |
| `exercise_id` | String | NO | Foreign Key $\rightarrow$ `exercise_catalog.exercise_id` | `INCLINE_DB_PRESS` |
| `set_order` | Integer| NO | Sequential index of the set in the workout (1-indexed) | `1` |
| `set_type` | String | NO | `W` (Warm-up), `S` (Working Set), `D` (Drop Set), `RP` (Rest-Pause) | `S` |
| `parent_set_id`| String | YES | Foreign Key $\rightarrow$ `workout_sets.set_id` (only if `set_type='D'`) | `S-20261010-01-03` |
| `load` | Float | YES | Resistance value (null if historical set count only) | `22.5` |
| `units` | String | NO | Standardized unit: `kg` (default), `lbs`, `bw` | `kg` |
| `reps` | Integer| YES | Repetitions completed (null if unknown) | `10` |
| `rir` | Float | YES | Reps in Reserve ($0.0 - 5.0$) | `1.5` |
| `rpe` | Float | YES | Rate of Perceived Exertion ($6.0 - 10.0$) | `8.5` |
| `rest_sec` | Integer| YES | Rest duration following set in seconds | `120` |
| `is_pr` | Integer| NO | `1` if personal record (load or rep), else `0` | `0` |
| `notes` | String | YES | Execution cues, tempo, or reason for termination | `Clean form` |

---

## 3. `DATA/exercise_catalog.csv`
Catalog of canonical exercises and biomechanical tags.

| Column | Type | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `exercise_id` | String | NO | Primary Key. Unique uppercase snake_case identifier | `INCLINE_DB_PRESS` |
| `exercise_name`| String | NO | Display name | `Incline Dumbbell Press` |
| `primary_muscle`| String| NO | Primary targeted muscle group | `Upper Chest` |
| `secondary_muscles`| String| YES | Comma-separated secondary muscle groups | `Anterior Delts, Triceps` |
| `equipment` | String | NO | `Dumbbell`, `Barbell`, `Cable`, `Machine`, `Bodyweight` | `Dumbbell` |
| `default_rep_range`| String| NO | Prescribed rep bracket | `8-12` |
| `default_rest_sec`| Integer| NO | Recommended rest interval between working sets | `150` |
| `load_convention`| String | NO | `per_hand` (DBs), `combined` (BB/Trap Bar), `machine_pin`, `bw_plus` | `per_hand` |
| `tier_priority`| String | NO | Goal priority classification: `Tier 1`, `Tier 2`, `Tier 3` | `Tier 1` |

---

## 4. `DATA/body_metrics.csv` & `BODY_METRICS/`
Daily/weekly anthropometric measurements and weight tracking.

| Column | Type | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `date` | Date | NO | ISO 8601 Date: `YYYY-MM-DD` | `2026-10-11` |
| `weight_kg` | Float | YES | Fasted morning scale weight in kg | `72.4` |
| `rolling_avg_7d`| Float | YES | 7-day trailing moving average of weight | `72.6` |
| `waist_cm` | Float | YES | Umbilicus waist circumference in cm | `84.5` |
| `chest_cm` | Float | YES | Mid-chest circumference in cm | `98.0` |
| `arms_cm` | Float | YES | Flexed upper arm circumference in cm | `34.5` |
| `shoulders_cm`| Float | YES | Bi-acromial shoulder circumference in cm | `114.0` |
| `notes` | String | YES | Measurement notes | `Fasted morning` |

---

## 5. `DATA/nutrition.csv`
Daily nutrition, hydration, and activity tracker.

| Column | Type | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `date` | Date | NO | ISO 8601 Date: `YYYY-MM-DD` | `2026-10-10` |
| `calories` | Integer| YES | Total daily energy intake in kcal | `1840` |
| `protein_g` | Float | YES | Total daily protein in grams | `148.0` |
| `carbs_g` | Float | YES | Total daily carbohydrates in grams | `185.0` |
| `fat_g` | Float | YES | Total daily dietary fat in grams | `52.0` |
| `steps` | Integer| YES | Daily pedometer step count | `6250` |
| `water_liters` | Float | YES | Daily fluid intake in liters | `3.2` |
| `adherence_flag`| Integer| NO | `1` if within target window ($\pm 100$ kcal), else `0` | `1` |
| `notes` | String | YES | Dietary notes or restaurant meals | `Whey + 4 eggs` |

---

## 6. `DATA/adherence.csv`
Weekly macro-level accountability and consistency tracker.

| Column | Type | Nullable | Description / Allowed Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `week_id` | String | NO | ISO Week format: `YYYY-Www` | `2026-W41` |
| `start_date` | Date | NO | Monday date of the week | `2026-10-05` |
| `end_date` | Date | NO | Sunday date of the week | `2026-10-11` |
| `planned_sessions`| Integer| NO | Number of training sessions programmed | `5` |
| `completed_sessions`| Integer| NO| Number of training sessions completed | `2` |
| `adherence_pct` | Float | NO | Percentage completed (`completed / planned * 100`) | `40.0` |
| `avg_steps` | Integer| YES | Weekly average daily steps | `6100` |
| `avg_protein_g`| Float | YES | Weekly average daily protein | `128.0` |
| `weight_delta_kg`| Float | YES | Week-over-week rolling weight delta | `-0.2` |
| `status` | String | NO | `ON_TRACK`, `AT_RISK`, `INCONSISTENT` | `INCONSISTENT` |
| `notes` | String | YES | Weekly coach summary notes | `Push only logged` |

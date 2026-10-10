---
name: workout-analysis
description: Analyzes an ingested workout against historical baselines, evaluates progressive overload, identifies bottlenecks, and provides strict coaching feedback.
---

# SKILL: WORKOUT ANALYSIS

## 1. PURPOSE & INVOCATION TRIGGER
Triggered immediately following workout ingestion or when evaluating training progression over recent sessions.

## 2. INPUTS & PREREQUISITES
- The newly ingested workout sets.
- Historical records from `DATA/workout_sets.csv` and previous workout markdown files.
- Current programming rules in `COACHING_RULES.md` and goals in `GOALS.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Retrieve Baselines**: For each exercise performed, query the most recent preceding session with the identical `exercise_id`.
2. **Double Progression Evaluation**:
   - Compare load, reps, and RIR.
   - Classify movement: **Progression** (increased reps or weight with stable form), **Maintained** (identical performance), or **Regression** (fewer reps or reduced load).
3. **Volume & Fatigue Audit**:
   - Calculate total hard working sets per target muscle group.
   - Detect excessive volume or redundant exercises (e.g. front raises combined with heavy pressing).
   - Evaluate exercise order: were priority muscles (lateral delts, upper chest) placed early?
4. **Formulate Coaching Evaluation**:
   - Follow the 7-stage coaching response protocol in `MASTER_COACH_PROMPT.md`.
   - Never offer empty encouragement; highlight genuine progressive overload or identify failure points.

## 4. OUTPUTS
- Coaching analysis section appended to the workout markdown log.
- Performance classification flags.
- Actionable feedback presented to trainee.

## 5. VALIDATION & ERROR HANDLING
- Ensure comparison is made against the **same exercise**, not an arbitrary previous day.
- Never equate dumbbell weight with barbell weight or compare different cable pulley stacks directly.

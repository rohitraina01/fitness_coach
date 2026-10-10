---
name: nutrition-review
description: Evaluates caloric intake, protein compliance, step count trends, and recalibrates maintenance calories based on empirical weight changes.
---

# SKILL: NUTRITION REVIEW

## 1. PURPOSE & INVOCATION TRIGGER
Triggered bi-weekly or monthly, or when scale weight trend deviates significantly from expectations.

## 2. INPUTS & PREREQUISITES
- Daily logs from `DATA/nutrition.csv`.
- Fasted morning weight entries from `DATA/body_metrics.csv` and `BODY_METRICS/weigh_ins.csv`.
- Guidelines from `NUTRITION_RULES.md` and client profile in `PROFILE.md`.

## 3. STEP-BY-STEP PROCEDURE
1. **Calorie & Macro Adherence Audit**:
   - Compute average daily caloric intake over the evaluation window.
   - Compute average daily protein intake in grams and g/kg.
   - Verify if protein meets the 145–155 g/day floor.
2. **Step Count & Activity Audit**:
   - Compare average daily steps against the 8,000–8,500 target.
3. **Maintenance Recalibration Equation**:
   - Energy balance equation:
     $$\Delta \text{Energy (kcal)} = \Delta \text{Weight (kg)} \times 7700 \text{ kcal/kg}$$
   - Calculate empirical maintenance:
     $$\text{Maintenance} = \text{Average Daily Intake} - \left(\frac{\Delta \text{Weight} \times 7700}{\text{Days}}\right)$$
   - If weight is stable and intake is 2,050 kcal, empirical maintenance $\approx 2,050$ kcal.
4. **Actionable Prescription**:
   - Adjust target calories by $\pm 100–150$ kcal only if weight change rate departs from the prescribed window for $\ge 3$ consecutive weeks.

## 4. OUTPUTS
- Updated monthly nutrition log in `NUTRITION_LOGS/YYYY/YYYY-MM/`.
- Updated status in `CURRENT_STATUS.md` and `PROFILE.md`.

## 5. VALIDATION & ERROR HANDLING
- Flag days with missing intake as unrecorded rather than assuming zero calories.
- Distinguish water weight swings (sodium, carbohydrates, stress) from true tissue changes.

import os
import csv
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")

class TestSchemas(unittest.TestCase):
    def test_workouts_schema(self):
        path = os.path.join(DATA_DIR, "workouts.csv")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ["workout_id", "date", "session_type", "session_name", "duration_min", "readiness_score", "status", "notes"]
            self.assertEqual(headers, expected)

    def test_workout_sets_schema(self):
        path = os.path.join(DATA_DIR, "workout_sets.csv")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ["set_id", "workout_id", "exercise_id", "set_order", "set_type", "parent_set_id", "load", "units", "reps", "rir", "rpe", "rest_sec", "is_pr", "notes"]
            self.assertEqual(headers, expected)

    def test_exercise_catalog_schema(self):
        path = os.path.join(DATA_DIR, "exercise_catalog.csv")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ["exercise_id", "exercise_name", "primary_muscle", "secondary_muscles", "equipment", "default_rep_range", "default_rest_sec", "load_convention", "tier_priority"]
            self.assertEqual(headers, expected)

    def test_body_metrics_schema(self):
        path = os.path.join(DATA_DIR, "body_metrics.csv")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ["date", "weight_kg", "rolling_avg_7d", "waist_cm", "chest_cm", "arms_cm", "shoulders_cm", "notes"]
            self.assertEqual(headers, expected)

    def test_nutrition_schema(self):
        path = os.path.join(DATA_DIR, "nutrition.csv")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ["date", "calories", "protein_g", "carbs_g", "fat_g", "steps", "water_liters", "adherence_flag", "notes"]
            self.assertEqual(headers, expected)

    def test_adherence_schema(self):
        path = os.path.join(DATA_DIR, "adherence.csv")
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ["week_id", "start_date", "end_date", "planned_sessions", "completed_sessions", "adherence_pct", "avg_steps", "avg_protein_g", "weight_delta_kg", "status", "notes"]
            self.assertEqual(headers, expected)

if __name__ == "__main__":
    unittest.main()

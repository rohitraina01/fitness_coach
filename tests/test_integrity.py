import os
import csv
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")

class TestIntegrity(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(DATA_DIR, "workouts.csv"), "r", encoding="utf-8") as f:
            self.workouts = list(csv.DictReader(f))
        with open(os.path.join(DATA_DIR, "workout_sets.csv"), "r", encoding="utf-8") as f:
            self.sets = list(csv.DictReader(f))
        with open(os.path.join(DATA_DIR, "exercise_catalog.csv"), "r", encoding="utf-8") as f:
            self.catalog = list(csv.DictReader(f))

    def test_unique_primary_keys(self):
        workout_ids = [w["workout_id"] for w in self.workouts]
        self.assertEqual(len(workout_ids), len(set(workout_ids)), "Duplicate workout_id detected")

        set_ids = [s["set_id"] for s in self.sets]
        self.assertEqual(len(set_ids), len(set(set_ids)), "Duplicate set_id detected")

        exercise_ids = [e["exercise_id"] for e in self.catalog]
        self.assertEqual(len(exercise_ids), len(set(exercise_ids)), "Duplicate exercise_id detected")

    def test_referential_integrity(self):
        valid_wids = {w["workout_id"] for w in self.workouts}
        valid_eids = {e["exercise_id"] for e in self.catalog}
        valid_sids = {s["set_id"] for s in self.sets}

        for s in self.sets:
            self.assertIn(s["workout_id"], valid_wids, f"Orphan set found: {s['set_id']}")
            self.assertIn(s["exercise_id"], valid_eids, f"Invalid exercise_id: {s['exercise_id']}")
            if s["parent_set_id"]:
                self.assertIn(s["parent_set_id"], valid_sids, f"Invalid parent_set_id in: {s['set_id']}")

    def test_valid_set_types_and_units(self):
        for s in self.sets:
            self.assertIn(s["set_type"], ["W", "S", "D", "RP"])
            self.assertIn(s["units"], ["kg", "lbs", "bw"])

if __name__ == "__main__":
    unittest.main()

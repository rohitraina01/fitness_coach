"""
test_coach_bridge.py - Automated Unit Tests for Mobile Bridge & Coach Agent
"""

import unittest
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from bridge import coach_agent
from bridge import server

class TestCoachBridge(unittest.TestCase):

    def test_instant_substitutions(self):
        prompt = "Shoulder pain on incline press, what should I substitute?"
        resp = coach_agent.generate_instant_coach_guidance(prompt)
        self.assertIn("COACH EXERCISE SUBSTITUTION", resp)
        self.assertIn("Dumbbell Press", resp)

    def test_instant_lat_substitution(self):
        prompt = "Lat pulldown feels weird, any alternative?"
        resp = coach_agent.generate_instant_coach_guidance(prompt)
        self.assertIn("Chest-Supported Neutral Row", resp)

    def test_instant_overload_targets(self):
        prompt = "What is my next weight on Incline DB press?"
        resp = coach_agent.generate_instant_coach_guidance(prompt)
        self.assertIn("OVERLOAD TARGETS", resp)
        self.assertIn("22.5 kg", resp)

    def test_instant_macros_guidance(self):
        prompt = "How much protein should I eat today?"
        resp = coach_agent.generate_instant_coach_guidance(prompt)
        self.assertIn("145–150g", resp)
        self.assertIn("1,850 kcal", resp)

    def test_instant_posture_guidance(self):
        prompt = "My APT and sitting posture need fixing"
        resp = coach_agent.generate_instant_coach_guidance(prompt)
        self.assertIn("ANTI-APT POSTURE RESTORATION", resp)
        self.assertIn("Half-Kneeling Hip Flexor Stretch", resp)

    def test_agent_task_lifecycle(self):
        prompt = "Unit test prompt for agent task"
        task = coach_agent.start_agent_task(prompt, mode="agent")
        self.assertTrue(task["task_id"].startswith("task_"))
        self.assertEqual(task["prompt"], prompt)

        fetched = coach_agent.get_agent_task(task["task_id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["task_id"], task["task_id"])

    def test_action_directive_posture(self):
        prog_path = os.path.join(BASE_DIR, "CURRENT_PROGRAM.md")
        orig_content = None
        if os.path.exists(prog_path):
            with open(prog_path, "r", encoding="utf-8") as f:
                orig_content = f.read()

        try:
            prompt = "add some more instruction in posture: maintain neutral pelvis while standing"
            task = {"events": []}
            handled, msg = coach_agent.handle_action_directive(prompt, task)
            self.assertTrue(handled)
            self.assertIn("DIRECTIVE EXECUTED", msg)
            self.assertIn("CURRENT_PROGRAM.md", msg)
        finally:
            if orig_content is not None:
                with open(prog_path, "w", encoding="utf-8") as f:
                    f.write(orig_content)

    def test_dummy_simulation(self):
        raw = "Lat pulldown 50kg x 10, 10, 8\nIncline DB press 20kg x 10, 10, 10"
        sim = server.simulate_dummy_workout(raw, "Pull")
        self.assertTrue(sim["success"])
        self.assertTrue(sim["dummy"])
        self.assertIn("DUMMY TEST SIMULATION", sim["coach_feedback"])

if __name__ == "__main__":
    unittest.main()

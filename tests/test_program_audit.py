import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import audit_program


class TestProgramAudit(unittest.TestCase):
    def test_program_and_next_workout_science_and_history(self):
        exit_code = audit_program.audit_program()
        self.assertEqual(exit_code, 0, "Program science/history/equipment audit failed")


if __name__ == "__main__":
    unittest.main()

import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "OUTPUTS", "mobile")
TXT_PATH = os.path.join(OUTPUT_DIR, "next_workout.txt")
HTML_PATH = os.path.join(OUTPUT_DIR, "next_workout.html")

class TestExport(unittest.TestCase):
    def test_mobile_exports_exist(self):
        self.assertTrue(os.path.exists(TXT_PATH), "Mobile txt export missing")
        self.assertTrue(os.path.exists(HTML_PATH), "Mobile html export missing")

    def test_mobile_exports_content(self):
        with open(TXT_PATH, "r", encoding="utf-8") as f:
            txt_content = f.read()
            self.assertIn("PULL A", txt_content)
            self.assertIn("Lat Pulldown", txt_content)

        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
            self.assertIn("PULL A", html_content)
            self.assertIn("set-tracker", html_content)

if __name__ == "__main__":
    unittest.main()

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
        next_md = os.path.join(BASE_DIR, "CURRENT_NEXT_WORKOUT.md")
        with open(next_md, "r", encoding="utf-8") as f:
            first_line = f.readline().replace("# NEXT WORKOUT:", "").strip()

        with open(TXT_PATH, "r", encoding="utf-8") as f:
            txt_content = f.read()
            self.assertIn(first_line, txt_content)

        with open(HTML_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
            self.assertIn(first_line, html_content)
            self.assertIn("set-tracker", html_content)

if __name__ == "__main__":
    unittest.main()

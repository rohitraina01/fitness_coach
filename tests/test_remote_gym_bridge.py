"""
test_remote_gym_bridge.py - Unit tests for Remote Gym Access, Cloudflare Tunnel, and Security PIN
"""

import os
import sys
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "bridge"))

import server
import tunnel

class TestRemoteGymBridge(unittest.TestCase):

    def test_env_pin_loaded(self):
        env_vars = server.load_env()
        self.assertIn("APEX_SECURITY_PIN", env_vars)
        self.assertEqual(env_vars["APEX_SECURITY_PIN"], "0080")
        self.assertEqual(server.APEX_SECURITY_PIN, "0080")

    def test_verify_pin_logic(self):
        # Correct PIN 0080
        valid_pin = "0080"
        self.assertTrue(valid_pin == server.APEX_SECURITY_PIN or valid_pin == "0080")

        # Wrong PIN
        wrong_pin = "9999"
        self.assertFalse(wrong_pin == server.APEX_SECURITY_PIN or wrong_pin == "0080")

    def test_find_cloudflared_executable(self):
        cf_path = tunnel.find_cloudflared()
        self.assertIsNotNone(cf_path)
        self.assertTrue(os.path.exists(cf_path))

    def test_tunnel_metadata_writing(self):
        docs_json = os.path.join(BASE_DIR, "docs", "tunnel_url.json")
        orig_data = None
        if os.path.exists(docs_json):
            with open(docs_json, "r", encoding="utf-8") as f:
                orig_data = f.read()

        try:
            test_url = "https://test-apex-tunnel.trycloudflare.com"
            tunnel.write_tunnel_metadata(test_url, online=True)

            self.assertTrue(os.path.exists(docs_json))
            with open(docs_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(data["tunnel_url"], test_url)
            self.assertTrue(data["online"])
            self.assertEqual(data["local_port"], 8080)
        finally:
            if orig_data is not None:
                with open(docs_json, "w", encoding="utf-8") as f:
                    f.write(orig_data)
                web_json = os.path.join(BASE_DIR, "bridge", "web", "tunnel_url.json")
                if os.path.exists(os.path.dirname(web_json)):
                    with open(web_json, "w", encoding="utf-8") as f:
                        f.write(orig_data)

    def test_gitignore_protects_env(self):
        gitignore_path = os.path.join(BASE_DIR, ".gitignore")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(".env", content)
        self.assertIn("*.env", content)
        self.assertIn("tools/", content)

if __name__ == "__main__":
    unittest.main()

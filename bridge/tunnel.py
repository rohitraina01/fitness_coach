"""
tunnel.py - Cloudflare Tunnel Manager for Remote Gym & Internet Access
Establishes a secure, global HTTPS tunnel from the trainee's home PC
to the outside internet so the phone app works at the gym over cellular/Wi-Fi.
Automatically updates docs/tunnel_url.json and pushes to GitHub Pages.
"""

import os
import sys
import json
import time
import re
import atexit
import signal
import subprocess
import threading
from datetime import datetime

# Windows console encoding safety
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
WEB_DIR = os.path.join(BRIDGE_DIR, "web")

PID_FILE = os.path.join(BRIDGE_DIR, ".tunnel.pid")
URL_FILE = os.path.join(BRIDGE_DIR, ".tunnel_url.txt")
DOCS_JSON = os.path.join(DOCS_DIR, "tunnel_url.json")
WEB_JSON = os.path.join(WEB_DIR, "tunnel_url.json")

PORT = 8080

def find_cloudflared():
    # 1. Local tools folder
    local_tool = os.path.join(BASE_DIR, "tools", "cloudflared.exe")
    if os.path.exists(local_tool):
        return local_tool
    
    # 2. System PATH
    try:
        res = subprocess.run(["where", "cloudflared"], capture_output=True, text=True)
        if res.returncode == 0:
            lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
            if lines:
                return lines[0]
    except Exception:
        pass
    
    # 3. Known Program Files paths
    for p in [
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared*\cloudflared.exe")
    ]:
        if os.path.exists(p):
            return p
            
    return None

def write_tunnel_metadata(url, online=True):
    now_str = datetime.now().isoformat()
    meta = {
        "tunnel_url": url,
        "online": online,
        "updated_at": now_str,
        "machine": os.environ.get("COMPUTERNAME", "Rohit-PC"),
        "local_port": PORT
    }
    
    # Write to runtime text file
    if online and url:
        with open(URL_FILE, "w", encoding="utf-8") as f:
            f.write(url)
    elif not online and os.path.exists(URL_FILE):
        try:
            os.remove(URL_FILE)
        except Exception:
            pass

    # Write to docs/ and bridge/web/
    for out_path in [DOCS_JSON, WEB_JSON]:
        try:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            print(f"[TUNNEL] Error writing metadata to {out_path}: {e}")

def push_tunnel_url_to_github():
    def _do_push():
        time.sleep(1) # Brief pause to ensure files flushed
        try:
            print("[TUNNEL] Auto-syncing tunnel URL to GitHub Pages...")
            subprocess.run(["git", "add", "docs/tunnel_url.json"], cwd=BASE_DIR, check=True)
            commit_res = subprocess.run(
                ["git", "commit", "-m", "chore: sync active cloud tunnel endpoint for gym access"],
                cwd=BASE_DIR, capture_output=True, text=True
            )
            if commit_res.returncode == 0:
                push_res = subprocess.run(
                    ["git", "push", "origin", "master"],
                    cwd=BASE_DIR, capture_output=True, text=True, timeout=25
                )
                if push_res.returncode == 0:
                    print("[TUNNEL] [OK] Tunnel URL published to GitHub Pages! Phone will auto-connect.")
                else:
                    print(f"[TUNNEL] Notice during git push: {push_res.stderr.strip()[:100]}")
            else:
                print("[TUNNEL] Tunnel URL already up-to-date on git.")
        except Exception as e:
            print(f"[TUNNEL] Git sync warning: {e}")

    t = threading.Thread(target=_do_push, daemon=True)
    t.start()

def clean_tunnel():
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass
    if os.path.exists(URL_FILE):
        try:
            os.remove(URL_FILE)
        except Exception:
            pass
    write_tunnel_metadata("", online=False)

atexit.register(clean_tunnel)

def start_tunnel():
    cloudflared = find_cloudflared()
    if not cloudflared:
        print("[TUNNEL ERROR] cloudflared.exe was not found. Please verify tools/cloudflared.exe exists.")
        return None

    print(f"[TUNNEL] Initializing Cloudflare secure HTTPS tunnel using: {cloudflared}")
    cmd = [cloudflared, "tunnel", "--url", f"http://127.0.0.1:{PORT}", "--no-autoupdate"]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(proc.pid))

    tunnel_url = None
    start_time = time.time()
    
    print("[TUNNEL] Establishing secure edge route with Cloudflare...")
    
    while time.time() - start_time < 20:
        line = proc.stderr.readline()
        if not line:
            time.sleep(0.1)
            continue
        
        m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if m:
            tunnel_url = m.group(0)
            break
            
        if proc.poll() is not None:
            print(f"[TUNNEL ERROR] cloudflared exited early with code {proc.returncode}")
            return None

    if tunnel_url:
        write_tunnel_metadata(tunnel_url, online=True)
        print("\n" + "=" * 72)
        print("  [ONLINE] CLOUDFLARE SECURE TUNNEL ACTIVE (REMOTE GYM ACCESS)")
        print("=" * 72)
        print(f"  Public Tunnel URL : {tunnel_url}")
        print(f"  GitHub Pages Web  : https://rohitraina01.github.io/fitness_coach/")
        print(f"  Security PIN      : 0080 (Set in .env)")
        print("=" * 72)
        print("  Your phone at the gym will now automatically connect to your PC")
        print("  over this encrypted HTTPS tunnel. Leave this process running.")
        print("=" * 72 + "\n")
        
        # Publish endpoint so phone automatically discovers it
        push_tunnel_url_to_github()
        return proc, tunnel_url
    else:
        print("[TUNNEL WARNING] Could not capture trycloudflare.com URL within timeout.")
        return proc, None

if __name__ == "__main__":
    res = start_tunnel()
    if res:
        proc, url = res
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n[TUNNEL] Shutting down tunnel...")
            proc.terminate()
            proc.wait()

"""
run_system.py - Unified Launcher for Fitness Coach Bridge & Cloud Tunnel
Runs both the local HTTP API Bridge (port 8080) and the Cloudflare Secure Tunnel,
enabling zero-configuration remote access for phone workouts from the gym.
"""

import os
import sys
import time
import subprocess
import signal

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(BRIDGE_DIR, "server.py")
TUNNEL_SCRIPT = os.path.join(BRIDGE_DIR, "tunnel.py")

def kill_existing_instances():
    """Ensure port 8080 and cloudflared are free before launching."""
    try:
        out = subprocess.check_output('netstat -aon | findstr ":8080" | findstr "LISTENING"', shell=True).decode()
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    except Exception:
        pass
    try:
        subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], capture_output=True)
    except Exception:
        pass

def main():
    print("=" * 72)
    print("  STARTING APEX FITNESS COACH SYSTEM (SERVER + CLOUD TUNNEL)")
    print("=" * 72)
    print(f"  Workspace: {BASE_DIR}")
    print()

    # Pre-clean port 8080 and old tunnels
    kill_existing_instances()
    time.sleep(0.5)

    # 1. Start Server Process
    print("[1/2] Starting HTTP Bridge Server on port 8080...")
    server_proc = subprocess.Popen([sys.executable, SERVER_SCRIPT], cwd=BASE_DIR)
    
    # Wait for server to bind port
    time.sleep(1.5)

    # 2. Start Cloudflare Tunnel
    print("[2/2] Launching Cloudflare Tunnel for Gym Remote Access...")
    tunnel_proc = subprocess.Popen([sys.executable, TUNNEL_SCRIPT], cwd=BASE_DIR)

    def shutdown(signum=None, frame=None):
        print("\n[SYSTEM] Terminating Bridge Server and Cloudflare Tunnel...")
        try:
            if tunnel_proc.poll() is None:
                tunnel_proc.terminate()
        except Exception:
            pass
        try:
            if server_proc.poll() is None:
                server_proc.terminate()
        except Exception:
            pass
        print("[SYSTEM] All services stopped cleanly.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        # Keep main thread alive monitoring children
        while True:
            time.sleep(1)
            if server_proc.poll() is not None:
                print(f"[SYSTEM] Notice: Server process exited (code {server_proc.returncode}). Auto-recovering...")
                time.sleep(1)
                server_proc = subprocess.Popen([sys.executable, SERVER_SCRIPT], cwd=BASE_DIR)
            if tunnel_proc.poll() is not None:
                print(f"[SYSTEM] Notice: Tunnel process exited (code {tunnel_proc.returncode}). Auto-recovering...")
                time.sleep(2)
                tunnel_proc = subprocess.Popen([sys.executable, TUNNEL_SCRIPT], cwd=BASE_DIR)
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()

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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SCRIPT = os.path.join(BRIDGE_DIR, "server.py")
TUNNEL_SCRIPT = os.path.join(BRIDGE_DIR, "tunnel.py")

def main():
    print("=" * 72)
    print("  STARTING APEX FITNESS COACH SYSTEM (SERVER + CLOUD TUNNEL)")
    print("=" * 72)
    print(f"  Workspace: {BASE_DIR}")
    print()

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
                print(f"[SYSTEM] Server process exited with code {server_proc.returncode}")
                break
            if tunnel_proc.poll() is not None:
                print(f"[SYSTEM] Tunnel process exited with code {tunnel_proc.returncode}")
                break
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()

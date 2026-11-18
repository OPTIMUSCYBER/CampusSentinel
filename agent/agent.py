import time
import psutil
import requests
import logging
from config import DEVICE_UID, BACKEND_URL, INTERVAL_SECONDS
from notice import show_first_run_notice
import threading
import tray

logging.basicConfig(level=logging.INFO)

# Global state for tray to read
latest_report = {"processes": [], "applications": []}

def collect_snapshot():
    processes = []
    # Simplified application list (in a real scenario, we'd query window titles or OS app APIs)
    applications = set()
    
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name:
                processes.append(name)
                # Heuristic for "application" vs background process: just a placeholder
                if name.endswith('.exe') and name not in ['svchost.exe', 'conhost.exe']:
                    applications.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Deduplicate processes for the payload size
    processes = list(set(processes))
    applications = list(applications)
    
    return {"processes": processes, "applications": applications}

def send_heartbeat():
    global latest_report
    while not tray.stop_event.is_set():
        try:
            snapshot = collect_snapshot()
            latest_report = snapshot
            
            res = requests.post(
                f"{BACKEND_URL}/api/v1/agent/heartbeat",
                headers={"x-device-uid": DEVICE_UID},
                json=snapshot,
                timeout=5
            )
            res.raise_for_status()
            logging.info(f"Heartbeat sent successfully to {BACKEND_URL}")
        except Exception as e:
            logging.error(f"Failed to send heartbeat: {e}")
            
        # Sleep in small increments to respond to stop_event quickly
        for _ in range(INTERVAL_SECONDS):
            if tray.stop_event.is_set():
                break
            time.sleep(1)

def run_agent():
    # Show notice on first run (we can just show it on every startup for this prototype)
    show_first_run_notice()
    
    # Start heartbeat thread
    t = threading.Thread(target=send_heartbeat, daemon=True)
    t.start()
    
    # Run tray icon (blocking)
    tray.run_tray()

if __name__ == "__main__":
    run_agent()

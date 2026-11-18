# CampusSentinel Agent

This is the Python agent that runs on monitored devices.

## Setup

1. Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the `agent/` directory:
   ```env
   DEVICE_UID=PC-101
   BACKEND_URL=http://127.0.0.1:8000
   INTERVAL_SECONDS=60
   ```
   *(Replace `PC-101` with the UID of a device you registered in the frontend)*

3. Run the agent:
   ```bash
   python agent.py
   ```

## Features
- **Transparency**: Shows a system tray icon. Users can right-click it to see what data is being collected.
- **Notice**: Shows a disclosure prompt on first run to ensure users are aware they are being monitored.
- **Reporting**: Collects a list of running applications and processes, and sends a heartbeat to the backend.

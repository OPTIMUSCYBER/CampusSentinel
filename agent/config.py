import os
from dotenv import load_dotenv

load_dotenv()

DEVICE_UID = os.environ.get("DEVICE_UID", "PC-101")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
INTERVAL_SECONDS = int(os.environ.get("INTERVAL_SECONDS", "60"))

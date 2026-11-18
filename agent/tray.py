import pystray
from PIL import Image, ImageDraw
import threading
import tkinter as tk
from tkinter import messagebox
import json

stop_event = threading.Event()

def create_image(width, height, color1, color2):
    # Create a simple icon (e.g. a shield or a dot)
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=color2
    )
    return image

def on_view_report(icon, item):
    import agent # Lazy import to avoid circular dependency issues
    
    # Show what was last reported in a dialog
    root = tk.Tk()
    root.withdraw()
    
    report = agent.latest_report
    apps = len(report.get("applications", []))
    procs = len(report.get("processes", []))
    
    msg = f"Last reported:\n\nApplications: {apps}\nProcesses: {procs}\n\n(See admin dashboard for full details)"
    messagebox.showinfo("Report Summary", msg)
    root.destroy()

def on_quit(icon, item):
    stop_event.set()
    icon.stop()

def run_tray():
    image = create_image(64, 64, 'black', 'white')
    
    menu = (
        pystray.MenuItem('Monitored by CampusSentinel', lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('View what\'s reported', on_view_report),
        pystray.MenuItem('Quit agent', on_quit)
    )
    
    icon = pystray.Icon("CampusSentinel", image, "CampusSentinel Agent", menu)
    icon.run()

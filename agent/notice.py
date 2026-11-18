import tkinter as tk
from tkinter import messagebox

def show_first_run_notice():
    root = tk.Tk()
    root.withdraw() # Hide the main window
    messagebox.showinfo(
        "CampusSentinel Notice",
        "This device is monitored by CampusSentinel for Campus IT.\n\n"
        "By clicking OK, you acknowledge that running applications and processes are reported to administration."
    )
    root.destroy()

if __name__ == "__main__":
    show_first_run_notice()

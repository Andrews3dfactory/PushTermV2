import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

def launch_pushterm():
    try:
        if sys.platform == "win32":
            subprocess.Popen(["start", "cmd", "/k", "python Pushterm_Terminal_Ui.py"], shell=True)
        else:
            subprocess.Popen(["x-terminal-emulator", "-e", "python3 Pushterm_Terminal_Ui.py"])
    except Exception as e:
        messagebox.showerror("Launch Failed", str(e))

root = tk.Tk()
root.title("Launch PushTerm")

launch_button = tk.Button(root, text="Launch PushTerm", command=launch_pushterm, font=("Segoe UI", 14), padx=20, pady=10)
launch_button.pack(padx=50, pady=50)

root.mainloop()

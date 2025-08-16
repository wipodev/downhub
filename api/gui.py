import tkinter as tk
from tkinter import scrolledtext, Menu
import requests
import os
import threading
import time

API_BASE = "http://127.0.0.1:8000"

def check_status(task_id):
    """Consulta periódicamente el estado del task."""
    while True:
        try:
            res = requests.get(f"{API_BASE}/status/{task_id}", timeout=5)
            if res.ok:
                data = res.json()
                status = data.get("status")
                if status == "completed":
                    log(f"✅ Download completed: {data.get('file')}")
                    break
                elif status == "error":
                    log(f"❌ Error: {data.get('error_msg')}")
                    break
            else:
                log(f"❌ Status check failed: {res.status_code} - {res.text}")
                break
            time.sleep(2)
        except Exception as e:
            log(f"❌ Error checking status: {e}")
            break

def download_video():
    url = url_entry.get().strip()
    if not url:
        log("Please enter a video URL.")
        return
    try:
        log(f"Starting download: {url}")
        res = requests.post(f"{API_BASE}/download", json={"url": url}, timeout=5)
        if res.ok:
            data = res.json()
            task_id = data.get("task_id")
            log(f"ℹ️ Download started (Task ID: {task_id})")
            url_entry.delete(0, tk.END)
            if task_id:
                threading.Thread(target=check_status, args=(task_id,), daemon=True).start()
        else:
            log(f"❌ Error: {res.status_code} - {res.text}")
    except Exception as e:
        log(f"❌ Error: {e}")

def log(message):
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, message + "\n")
    log_area.see(tk.END)
    log_area.config(state=tk.DISABLED)

def paste_from_clipboard(event=None):
    try:
        url_entry.delete(0, tk.END)
        url_entry.insert(tk.END, root.clipboard_get())
    except tk.TclError:
        pass

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

# --- UI Setup ---
root = tk.Tk()
root.title("DownHub GUI")
root.geometry("500x300")
root.resizable(False, False)

# Set icon
icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon2.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, pady=5)

# Label + Entry
tk.Label(main_frame, text="Video URL:", font=("Segoe UI", 10, "bold")).pack(pady=5)

url_entry = tk.Entry(main_frame, width=60)
url_entry.pack(pady=5)
url_entry.focus()

# Context menu for paste
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Paste", command=paste_from_clipboard)
url_entry.bind("<Button-3>", show_context_menu)

# Download button
download_btn = tk.Button(main_frame, text="Download", width=15, command=download_video)
download_btn.pack(pady=5)

# Log area + footer juntos
log_frame = tk.Frame(main_frame)
log_frame.pack(fill="both", expand=True, pady=(10, 0))

log_area = scrolledtext.ScrolledText(
    log_frame, wrap=tk.WORD, width=60, height=10, state=tk.DISABLED
)
log_area.pack(side="top", fill="both", expand=True)

footer_text = "Ensure DownHubService is running before using this GUI."
tk.Label(
    log_frame,
    text=footer_text,
    font=("Segoe UI", 8),
    wraplength=460,
    justify="center"
).pack(side="bottom", pady=(2, 5))

root.mainloop()

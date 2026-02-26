import os
import shutil
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ================= FILE TYPES =================
FILE_TYPES = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx"],
    "Audio": [".mp3", ".wav", ".aac"],
}

# ================= HELPERS =================
def get_category(extension):
    extension = extension.lower()
    for category, extensions in FILE_TYPES.items():
        if extension in extensions:
            return category
    return "Others"


def scan_files(folder_path):
    files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            files.append(filename)
    return files


def organize_folder(folder_path, preview=False):
    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "Folder does not exist.")
        return

    files = scan_files(folder_path)
    total_files = len(files)

    if total_files == 0:
        messagebox.showinfo("Info", "No files found.")
        return

    moved = 0
    progress["maximum"] = total_files
    summary = {}

    for index, filename in enumerate(files, start=1):
        file_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1]
        category = get_category(ext)

        summary[category] = summary.get(category, 0) + 1

        category_folder = os.path.join(folder_path, category)
        os.makedirs(category_folder, exist_ok=True)

        new_path = os.path.join(category_folder, filename)

        # duplicate protection
        counter = 1
        base, extension = os.path.splitext(filename)
        while os.path.exists(new_path):
            new_filename = f"{base}_{counter}{extension}"
            new_path = os.path.join(category_folder, new_filename)
            counter += 1

        if preview:
            log(f"[PREVIEW] {filename} → {category}")
        else:
            shutil.move(file_path, new_path)
            log(f"Moved: {filename} → {category}")
            moved += 1

        # progress update
        progress["value"] = index
        percent.set(f"{int((index/total_files)*100)}%")
        count_label.config(text=f"Processed: {index}/{total_files}")
        root.update()

    summary_text = "\n".join([f"{k}: {v}" for k, v in summary.items()])
    log("\n=== SUMMARY ===")
    log(summary_text)

    if preview:
        messagebox.showinfo("Preview Complete", f"Scanned {total_files} files.")
    else:
        messagebox.showinfo("Done", f"Organized {moved} files.")


def log(message):
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)


def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)


def run_preview():
    log_box.delete(1.0, tk.END)
    progress["value"] = 0
    percent.set("0%")
    organize_folder(folder_var.get(), preview=True)


def run_organize():
    log_box.delete(1.0, tk.END)
    progress["value"] = 0
    percent.set("0%")
    organize_folder(folder_var.get(), preview=False)

# ================= AUTO SCHEDULER =================
scheduler_running = False

def auto_cleanup_loop(folder_path, interval_minutes):
    global scheduler_running
    scheduler_running = True

    while scheduler_running:
        log("🤖 Auto-cleanup running...")
        try:
            organize_folder(folder_path, preview=False)
        except Exception as e:
            log(f"Scheduler error: {e}")

        for _ in range(interval_minutes * 60):
            if not scheduler_running:
                break
            time.sleep(1)

def start_scheduler():
    interval = interval_var.get()
    try:
        interval = int(interval)
        if interval <= 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Enter valid minutes.")
        return

    thread = threading.Thread(
        target=auto_cleanup_loop,
        args=(folder_var.get(), interval),
        daemon=True
    )
    thread.start()
    log(f"🚀 Auto-cleanup started every {interval} minutes")

def stop_scheduler():
    global scheduler_running
    scheduler_running = False
    log("🛑 Auto-cleanup stopped")

# ================= NEON CYBER UI =================
root = tk.Tk()
root.title("AI File Organizer — Neon Future")
root.geometry("760x600")
root.configure(bg="#020617")

style = ttk.Style()
style.theme_use("default")
style.configure("TProgressbar", thickness=14)

folder_var = tk.StringVar(value=str(Path.home() / "Downloads"))
percent = tk.StringVar(value="0%")
interval_var = tk.StringVar(value="10")

NEON_GREEN = "#00ff9c"
NEON_BLUE = "#00e5ff"
NEON_PURPLE = "#8b5cf6"
CARD_BG = "#020617"

# ===== Title =====
title = tk.Label(
    root,
    text="AI FILE ORGANIZER // NEON EDITION",
    font=("Segoe UI", 20, "bold"),
    fg=NEON_GREEN,
    bg=CARD_BG
)
title.pack(pady=14)

# ===== Folder Row =====
frame = tk.Frame(root, bg=CARD_BG)
frame.pack(pady=5)

folder_entry = tk.Entry(frame, textvariable=folder_var, width=60)
folder_entry.pack(side=tk.LEFT, padx=6)

browse_btn = tk.Button(
    frame,
    text="Browse",
    command=choose_folder,
    bg=NEON_BLUE,
    fg="black",
    relief="flat"
)
browse_btn.pack(side=tk.LEFT)

# ===== Buttons =====
btn_frame = tk.Frame(root, bg=CARD_BG)
btn_frame.pack(pady=10)

preview_btn = tk.Button(
    btn_frame,
    text="🔍 Preview Scan",
    command=run_preview,
    bg=NEON_PURPLE,
    fg="white",
    width=16,
    relief="flat"
)
preview_btn.pack(side=tk.LEFT, padx=10)

organize_btn = tk.Button(
    btn_frame,
    text="⚡ Organize Now",
    command=run_organize,
    bg=NEON_GREEN,
    fg="black",
    width=16,
    relief="flat"
)
organize_btn.pack(side=tk.LEFT, padx=10)

# ===== Scheduler Panel =====
sched_frame = tk.Frame(root, bg=CARD_BG)
sched_frame.pack(pady=6)

tk.Label(
    sched_frame,
    text="Auto-clean every (minutes):",
    fg="white",
    bg=CARD_BG
).pack(side=tk.LEFT, padx=5)

interval_entry = tk.Entry(sched_frame, textvariable=interval_var, width=6)
interval_entry.pack(side=tk.LEFT)

start_btn = tk.Button(
    sched_frame,
    text="▶ Start Auto",
    command=start_scheduler,
    bg=NEON_BLUE,
    fg="black",
    relief="flat"
)
start_btn.pack(side=tk.LEFT, padx=6)

stop_btn = tk.Button(
    sched_frame,
    text="■ Stop",
    command=stop_scheduler,
    bg="#ef4444",
    fg="white",
    relief="flat"
)
stop_btn.pack(side=tk.LEFT)

# ===== Progress =====
progress = ttk.Progressbar(root, length=520)
progress.pack(pady=8)

count_label = tk.Label(
    root,
    text="Processed: 0/0",
    fg="white",
    bg=CARD_BG
)
count_label.pack()

percent_label = tk.Label(
    root,
    textvariable=percent,
    font=("Segoe UI", 12, "bold"),
    fg=NEON_GREEN,
    bg=CARD_BG
)
percent_label.pack(pady=4)

# ===== Log Box =====
log_box = tk.Text(
    root,
    height=18,
    bg="#010409",
    fg=NEON_BLUE,
    insertbackground=NEON_GREEN,
    font=("Consolas", 10)
)
log_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

root.mainloop()
import shutil
import csv
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

FOLDER_RULES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Audio": [".mp3", ".wav", ".flac", ".aac"],
    "Archives": [".zip", ".tar", ".gz", ".rar"],
    "Code": [".py", ".js", ".html", ".css", ".json"],
    "Shortcuts": [".url", ".lnk"],
}

def get_destination(extension: str) -> str:
    for folder, extensions in FOLDER_RULES.items():
        if extension.lower() in extensions:
            return folder
    return "Other"

class OrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.observer = None

        # Title
        tk.Label(root, text="File Organizer", font=("Helvetica", 20, "bold")).pack(pady=15)

        # Folder selection
        frame = tk.Frame(root)
        frame.pack(pady=5, padx=20, fill="x")
        self.folder_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.folder_var, width=50, font=("Helvetica", 10)).pack(side="left", padx=5)
        tk.Button(frame, text="Browse", command=self.browse_folder).pack(side="left")

        # Dry run checkbox
        self.dry_run_var = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="Dry run (preview only)", variable=self.dry_run_var, font=("Helvetica", 10)).pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Organize Now", width=15, bg="#4CAF50", fg="white",
                  font=("Helvetica", 11, "bold"), command=self.organize).pack(side="left", padx=10)
        self.watch_btn = tk.Button(btn_frame, text="Start Watching", width=15, bg="#2196F3", fg="white",
                  font=("Helvetica", 11, "bold"), command=self.toggle_watch)
        self.watch_btn.pack(side="left", padx=10)

        # Log output
        tk.Label(root, text="Activity Log:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=20)
        self.log = scrolledtext.ScrolledText(root, height=15, width=70, font=("Courier", 9), state="disabled")
        self.log.pack(padx=20, pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def log_message(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def organize(self):
        source = self.folder_var.get()
        if not source:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return

        source_path = Path(source)
        dry_run = self.dry_run_var.get()
        log = []

        self.log_message(f"\n--- {'DRY RUN' if dry_run else 'ORGANIZING'} ---")

        for file in source_path.iterdir():
            if file.is_file():
                dest_folder = get_destination(file.suffix)
                dest_path = source_path / dest_folder / file.name
                self.log_message(f"{'[DRY RUN] ' if dry_run else ''}Moving {file.name} → {dest_folder}/")
                if not dry_run:
                    (source_path / dest_folder).mkdir(exist_ok=True)
                    shutil.move(str(file), str(dest_path))
                log.append({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             "file": file.name, "destination": dest_folder, "dry_run": dry_run})

        self.log_message(f"\nFiles processed: {len(log)}")
        for folder in set(e['destination'] for e in log):
            count = sum(1 for e in log if e['destination'] == folder)
            self.log_message(f"  {folder}: {count} file(s)")

        if not dry_run and log:
            log_path = source_path / "organizer_log.csv"
            with open(log_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "file", "destination", "dry_run"])
                if log_path.stat().st_size == 0:
                    writer.writeheader()
                writer.writerows(log)
            self.log_message("Log saved to organizer_log.csv")

    def toggle_watch(self):
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.watch_btn.config(text="Start Watching", bg="#2196F3")
            self.log_message("Stopped watching.")
        else:
            source = self.folder_var.get()
            if not source:
                messagebox.showwarning("No folder", "Please select a folder first.")
                return
            self.watch_btn.config(text="Stop Watching", bg="#f44336")
            self.log_message(f"Watching {source} for new files...")
            handler = GUIHandler(source, self.dry_run_var.get(), self.log_message)
            self.observer = Observer()
            self.observer.schedule(handler, source, recursive=False)
            self.observer.start()

class GUIHandler(FileSystemEventHandler):
    def __init__(self, source, dry_run, log_func):
        self.source = source
        self.dry_run = dry_run
        self.log = log_func

    def on_created(self, event):
        if not event.is_directory:
            file = Path(event.src_path)
            dest_folder = get_destination(file.suffix)
            dest_path = Path(self.source) / dest_folder / file.name
            self.log(f"{'[DRY RUN] ' if self.dry_run else ''}New file: {file.name} → {dest_folder}/")
            if not self.dry_run:
                (Path(self.source) / dest_folder).mkdir(exist_ok=True)
                shutil.move(str(file), str(dest_path))

if __name__ == "__main__":
    root = tk.Tk()
    app = OrganizerApp(root)
    root.mainloop()
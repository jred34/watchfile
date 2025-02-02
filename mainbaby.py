import os
import time
import queue
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SimpleFileMonitorHandler(FileSystemEventHandler):
    """Handles file system events and logs changes in a simplified manner."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def log_event(self, event_type, event_path):
        """Puts log messages in the queue for GUI updates."""
        message = f"{event_type}: {event_path}"
        self.log_queue.put(message)

    def on_created(self, event):
        """Logs when a file or folder is created."""
        self.log_event("📂 Created", event.src_path)

    def on_deleted(self, event):
        """Logs when a file or folder is deleted."""
        self.log_event("🗑 Deleted", event.src_path)

    def on_modified(self, event):
        """Logs when a file is modified (deep tracking)."""
        if not event.is_directory:
            self.log_event("✏️ File Modified", event.src_path)

    def on_moved(self, event):
        """Logs when a file or folder is renamed or moved."""
        self.log_event("🔄 Moved/Renamed", f"{event.src_path} → {event.dest_path}")

class FileMonitorApp:
    """GUI Application for Simplified File Monitoring."""

    def __init__(self, root):
        self.root = root
        self.root.title("File System Monitor")
        self.root.geometry("700x500")

        # Create a queue for event logs
        self.log_queue = queue.Queue()

        # Title Label
        self.label = tk.Label(root, text="📂 File System Monitor", font=("Arial", 14))
        self.label.pack(pady=5)

        # Folder Selection Button
        self.folder_button = tk.Button(root, text="Select Folder to Monitor", command=self.select_folder)
        self.folder_button.pack(pady=5)

        # Scrollable Log Window
        self.log_widget = scrolledtext.ScrolledText(root, width=80, height=20)
        self.log_widget.pack(pady=5)

        # Start Monitoring Button
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        # Save Logs Button
        self.save_button = tk.Button(root, text="Save Logs", command=self.save_logs)
        self.save_button.pack(pady=5)

        self.monitoring_path = None
        self.process_log_queue()

    def select_folder(self):
        """Allows the user to choose a folder dynamically."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.monitoring_path = folder_selected
            self.log_widget.insert(tk.END, f"📂 Selected folder: {self.monitoring_path}\n")
            self.start_button.config(state=tk.NORMAL)

    def process_log_queue(self):
        """Continuously updates the GUI with new log messages."""
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_widget.insert(tk.END, message + "\n")
            self.log_widget.see(tk.END)
        self.root.after(100, self.process_log_queue)

    def start_monitoring(self):
        """Starts monitoring the selected directory for file system changes."""
        if not self.monitoring_path:
            self.log_widget.insert(tk.END, "⚠️ Please select a folder first!\n")
            return

        self.log_widget.insert(tk.END, f"🔍 Monitoring started on: {self.monitoring_path}\n")

        event_handler = SimpleFileMonitorHandler(self.log_queue)
        observer = Observer()
        observer.schedule(event_handler, self.monitoring_path, recursive=True)
        observer.start()

        def run_observer():
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                self.log_queue.put("🛑 Monitoring stopped.")

            observer.join()

        thread = threading.Thread(target=run_observer, daemon=True)
        thread.start()

    def save_logs(self):
        """Saves log messages to a text file."""
        logs = self.log_widget.get("1.0", tk.END)
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as file:
                file.write(logs)
            self.log_widget.insert(tk.END, f"✅ Logs saved to {save_path}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMonitorApp(root)
    root.mainloop()

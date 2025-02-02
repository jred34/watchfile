import time
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMonitorHandler(FileSystemEventHandler):
    """Handles file system events and adds them to a queue for GUI updates."""

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue  # Queue to send logs to the GUI

    def log_event(self, event_type, event_path):
        """Adds a detailed event log to the queue, ensuring full folder paths are shown."""
        folder_path, file_name = event_path.rsplit("\\", 1) if "\\" in event_path else ("Root Folder", event_path)
        message = f"{event_type}: {file_name} in {folder_path}"
        self.log_queue.put(message)

    def on_created(self, event):
        """Logs when a file or folder is created."""
        if event.is_directory:
            self.log_event("📁 New Folder Created", event.src_path)
        else:
            self.log_event("📄 New File Created", event.src_path)

    def on_deleted(self, event):
        """Logs when a file or folder is deleted."""
        if event.is_directory:
            self.log_event("🗑 Folder Deleted", event.src_path)
        else:
            self.log_event("🗑 File Deleted", event.src_path)

    def on_modified(self, event):
        """Logs when a file or folder is modified."""
        import os
        if event.is_directory:
            self.log_event("✏️ Folder Modified", event.src_path)
        else:
            file_size = os.path.getsize(event.src_path)  # Get the updated file size
            self.log_event("✏️ File Modified (New Content)" ,event.src_path)

    def on_moved(self, event):
        """Logs when a file or folder is renamed or moved."""
        old_folder_path, old_name = event.src_path.rsplit("\\", 1) if "\\" in event.src_path else (
        "Root Folder", event.src_path)
        new_folder_path, new_name = event.dest_path.rsplit("\\", 1) if "\\" in event.dest_path else (
        "Root Folder", event.dest_path)

        message = f"🔄 Moved/Renamed: {old_name} in {old_folder_path} → {new_name} in {new_folder_path}"
        self.log_queue.put(message)

class FileMonitorApp:
    """GUI Application for File Monitoring."""

    def __init__(self, root):
        self.root = root
        self.root.title("File System Monitor")
        self.root.geometry("600x400")

        # Create a queue for event logs
        self.log_queue = queue.Queue()

        # Title Label
        self.label = tk.Label(root, text="📂 File System Monitor", font=("Arial", 14))
        self.label.pack(pady=5)

        # Scrollable Log Window
        self.log_widget = scrolledtext.ScrolledText(root, width=70, height=15)
        self.log_widget.pack(pady=5)

        # Start Monitoring Button
        self.start_button = tk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=5)

        # Continuously update the GUI with new log messages
        self.process_log_queue()

    def process_log_queue(self):
        """Continuously checks the queue for new log messages and updates the GUI."""
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_widget.insert(tk.END, message + "\n")
            self.log_widget.see(tk.END)  # Auto-scroll to latest log

        self.root.after(100, self.process_log_queue)  # Check queue every 100ms

    def start_monitoring(self):
        """Starts monitoring the file system for changes."""
        path_to_monitor = "C:/Users/DIPEN/PycharmProjects/filesystem"  # Your project folder
        self.log_widget.insert(tk.END, f"🔍 Monitoring started on: {path_to_monitor}\n")
        self.log_widget.see(tk.END)

        event_handler = FileMonitorHandler(self.log_queue)
        observer = Observer()
        observer.schedule(event_handler, path_to_monitor, recursive=True)
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

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMonitorApp(root)
    root.mainloop()

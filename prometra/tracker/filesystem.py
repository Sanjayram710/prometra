import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PrometraFSEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_any_event(self, event):
        if event.is_directory:
            return
        # Basic debouncing logic would go here
        self.callback(event)

class FilesystemTracker:
    def __init__(self, watch_dir: str, callback):
        self.watch_dir = watch_dir
        self.callback = callback
        self.observer = Observer()
        self.handler = PrometraFSEventHandler(self.callback)

    def start(self):
        self.observer.schedule(self.handler, self.watch_dir, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

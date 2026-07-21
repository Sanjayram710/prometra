import os
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from prometra.core.time import utcnow

class PrometraFSEventHandler(FileSystemEventHandler):
    def __init__(self, callback, watch_dir: str):
        self.callback = callback
        self.watch_dir = watch_dir

    def on_any_event(self, event):
        if event.is_directory:
            return
            
        # Ignore .git and .prometra
        if ".git" in event.src_path or ".prometra" in event.src_path:
            return
            
        rel_path = os.path.relpath(event.src_path, self.watch_dir)
        norm_path = rel_path.replace("\\", "/")
        
        event_info = {
            "type": "filesystem",
            "operation": event.event_type,
            "path": event.src_path,
            "normalized_relative_path": norm_path,
            "timestamp": utcnow()
        }
        self.callback(event_info)

class FilesystemTracker:
    def __init__(self, watch_dir: str, timeline_engine, session_id: str, project_id: str):
        self.watch_dir = watch_dir
        self.timeline_engine = timeline_engine
        self.session_id = session_id
        self.project_id = project_id
        
        self.queue = []
        self.lock = threading.Lock()
        self.debounce_timer = None
        self.debounce_ms = 500
        
        self.observer = Observer()
        self.handler = PrometraFSEventHandler(self._queue_event, self.watch_dir)

    def _queue_event(self, event_info: dict):
        with self.lock:
            self.queue.append(event_info)
            if self.debounce_timer:
                self.debounce_timer.cancel()
            self.debounce_timer = threading.Timer(self.debounce_ms / 1000.0, self._flush)
            self.debounce_timer.start()

    def _flush(self):
        with self.lock:
            if not self.queue:
                return
            events_to_process = self.queue[:]
            self.queue = []
            
        # Basic debouncing: collapse same file + same operation within the window
        deduped = {}
        for ev in events_to_process:
            key = (ev["normalized_relative_path"], ev["operation"])
            deduped[key] = ev
            
        for ev in deduped.values():
            ev["session_id"] = self.session_id
            ev["project_id"] = self.project_id
            ev["source"] = "filesystem"
            ev["summary"] = f"File {ev['operation']}: {ev['normalized_relative_path']}"
            self.timeline_engine.append_event(ev)

    def start(self):
        self.observer.schedule(self.handler, self.watch_dir, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
        if self.debounce_timer:
            self.debounce_timer.cancel()
        self._flush()

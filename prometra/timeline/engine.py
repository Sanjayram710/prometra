from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel

class TimelineEngine:
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def append_event(self, event_data: dict):
        db = self.storage.get_session()
        try:
            max_seq = db.query(TimelineEventModel).count()
            
            tl_event = TimelineEventModel(
                normalized_event_type=event_data.get("type", "unknown"),
                timestamp=event_data.get("timestamp"),
                sequence=max_seq + 1,
                source=event_data.get("source", "system"),
                summary=event_data.get("summary", "")
            )
            db.add(tl_event)
            db.commit()
        finally:
            db.close()

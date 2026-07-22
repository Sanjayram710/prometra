from typing import List, Dict, Any, Optional
from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import SessionModel, TimelineEventModel
from prometra.timeline.engine import TimelineEngine
from prometra.timeline.queries import TimelineQueryEngine
from prometra.timeline.filters import TimelineFilter

class ReplayEngine:
    """Engine for querying session history and streaming events for session replay."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
        self.query_engine = TimelineQueryEngine(storage)
        self.timeline_engine = TimelineEngine(storage)

    def resolve_session_id(self, session_id: Optional[str] = None, latest: bool = False) -> Optional[str]:
        """Resolve target session ID by explicit ID or latest session."""
        db = self.storage.get_session()
        try:
            if session_id:
                session = db.query(SessionModel).filter_by(session_id=session_id).first()
                if session:
                    return session.session_id
                # Fallback: check if session_id exists in timeline_events
                tl = db.query(TimelineEventModel).filter_by(session_id=session_id).first()
                if tl:
                    return tl.session_id
                return session_id

            if latest or not session_id:
                latest_session = db.query(SessionModel).order_by(SessionModel.start_ts.desc()).first()
                if latest_session:
                    return latest_session.session_id
                latest_tl = db.query(TimelineEventModel).filter(TimelineEventModel.session_id.isnot(None)).order_by(TimelineEventModel.id.desc()).first()
                if latest_tl:
                    return latest_tl.session_id
            return None
        finally:
            db.close()

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session metadata and metric counts."""
        db = self.storage.get_session()
        try:
            sess = db.query(SessionModel).filter_by(session_id=session_id).first()
            events = self.query_engine.fetch_events(TimelineFilter(session_id=session_id))
            
            duration = sess.duration_seconds if sess and sess.duration_seconds else 0
            if not duration and len(events) > 1:
                start = events[0].timestamp
                end = events[-1].timestamp
                if start and end:
                    duration = int(abs((end - start).total_seconds()))

            start_time = str(sess.start_ts) if sess and sess.start_ts else (str(events[0].timestamp) if events else "")
            
            return {
                "session_id": session_id,
                "start_ts": start_time,
                "duration_seconds": duration,
                "total_events": len(events),
                "status": sess.status if sess else "completed"
            }
        finally:
            db.close()

    def get_session_events(self, session_id: str) -> List[TimelineEventModel]:
        """Fetch all chronological events for the specified session."""
        filters = TimelineFilter(session_id=session_id, limit=None, reverse=False)
        return self.query_engine.fetch_events(filters)

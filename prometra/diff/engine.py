import os
import difflib
from typing import List, Optional, Tuple, Dict, Any

from prometra.storage.sqlite import SQLiteStorage
from prometra.storage.models import TimelineEventModel, FilesystemEventModel, AiEventModel, GitEventModel, SessionModel
from prometra.diff.models import FileVersion, DiffResult, DiffOptions

class DiffEngine:
    """Engine for querying file event history and computing local unified diffs."""

    def __init__(self, storage: SQLiteStorage):
        self.storage = storage

    def _normalize_path(self, path: str) -> str:
        """Normalize file path for consistent matching."""
        if not path:
            return ""
        return os.path.normpath(path).replace("\\", "/").lower()

    def _extract_content_from_event(
        self,
        tl_event: TimelineEventModel,
        fs_event: Optional[FilesystemEventModel] = None,
        ai_event: Optional[AiEventModel] = None,
        git_event: Optional[GitEventModel] = None,
        file_path: Optional[str] = None
    ) -> Optional[str]:
        """Extract inline content associated with an event record if available."""
        if ai_event and ai_event.extra_metadata:
            meta = ai_event.extra_metadata
            for key in ("content", "file_content", "code", "snapshot", "after_content", "text"):
                if key in meta and isinstance(meta[key], str):
                    return meta[key]

        if file_path and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read()
            except Exception:
                pass

        return None

    def get_file_events(self, file_path: str, session_id: Optional[str] = None) -> List[FileVersion]:
        """Retrieve chronologically ordered FileVersions from SQLite event history."""
        target_norm = self._normalize_path(file_path)
        filename = os.path.basename(file_path).lower()
        
        db = self.storage.get_session()
        try:
            if session_id:
                sess_check = db.query(SessionModel).filter_by(session_id=session_id).first()
                if not sess_check:
                    tl_check = db.query(TimelineEventModel).filter_by(session_id=session_id).first()
                    if not tl_check:
                        raise ValueError(f"Session '{session_id}' not found.")

            fs_query = db.query(FilesystemEventModel)
            if session_id:
                fs_query = fs_query.filter(FilesystemEventModel.session_id == session_id)
            fs_records = fs_query.all()

            fs_map: Dict[str, FilesystemEventModel] = {}
            matching_fs_ids = set()
            for r in fs_records:
                fs_map[r.event_id] = r
                r_norm = self._normalize_path(r.normalized_relative_path or r.path)
                r_path = self._normalize_path(r.path)
                r_filename = os.path.basename(r.path or "").lower()
                if r_norm == target_norm or r_path == target_norm or r_norm.endswith(target_norm) or r_filename == filename:
                    matching_fs_ids.add(r.event_id)

            ai_query = db.query(AiEventModel)
            if session_id:
                ai_query = ai_query.filter(AiEventModel.session_id == session_id)
            ai_records = ai_query.all()

            ai_map: Dict[str, AiEventModel] = {}
            matching_ai_ids = set()
            for r in ai_records:
                ai_map[r.event_id] = r
                if r.extra_metadata and isinstance(r.extra_metadata, dict):
                    p = r.extra_metadata.get("path") or r.extra_metadata.get("file") or r.extra_metadata.get("file_path")
                    if p:
                        p_norm = self._normalize_path(str(p))
                        if p_norm == target_norm or p_norm.endswith(target_norm) or os.path.basename(str(p)).lower() == filename:
                            matching_ai_ids.add(r.event_id)

            git_query = db.query(GitEventModel)
            git_records = git_query.all()
            git_map: Dict[str, GitEventModel] = {r.event_id: r for r in git_records}

            tl_query = db.query(TimelineEventModel)
            if session_id:
                tl_query = tl_query.filter(TimelineEventModel.session_id == session_id)
            tl_events = tl_query.order_by(TimelineEventModel.id.asc()).all()

            file_versions: List[FileVersion] = []
            seen_event_ids = set()

            for tl in tl_events:
                is_match = False
                related = tl.related_event_ids or []
                fs_rec = None
                ai_rec = None
                git_rec = None

                for rel_id in related:
                    if rel_id in matching_fs_ids:
                        is_match = True
                        fs_rec = fs_map.get(rel_id)
                    elif rel_id in matching_ai_ids:
                        is_match = True
                        ai_rec = ai_map.get(rel_id)
                    elif rel_id in fs_map:
                        fs_rec = fs_map.get(rel_id)
                    elif rel_id in ai_map:
                        ai_rec = ai_map.get(rel_id)
                    elif rel_id in git_map:
                        git_rec = git_map.get(rel_id)

                if not is_match:
                    summary_lower = (tl.summary or "").lower()
                    if target_norm in summary_lower or filename in summary_lower:
                        is_match = True

                if is_match and tl.id not in seen_event_ids:
                    seen_event_ids.add(tl.id)
                    content = self._extract_content_from_event(
                        tl_event=tl,
                        fs_event=fs_rec,
                        ai_event=ai_rec,
                        git_event=git_rec,
                        file_path=file_path
                    )
                    
                    if content is None and ai_rec and ai_rec.extra_metadata:
                        for k in ("before_content", "old_content"):
                            if k in ai_rec.extra_metadata:
                                content = ai_rec.extra_metadata[k]
                                break

                    version = FileVersion(
                        event_id=tl.id,
                        file_path=file_path,
                        content=content if content is not None else "",
                        timestamp=tl.timestamp,
                        session_id=tl.session_id
                    )
                    file_versions.append(version)

            if not file_versions:
                for fs_id in sorted(list(matching_fs_ids)):
                    fs_rec = fs_map.get(fs_id)
                    if fs_rec:
                        content = self._extract_content_from_event(
                            tl_event=None,
                            fs_event=fs_rec,
                            file_path=file_path
                        )
                        v = FileVersion(
                            event_id=len(file_versions) + 1,
                            file_path=file_path,
                            content=content if content is not None else "",
                            timestamp=fs_rec.timestamp,
                            session_id=fs_rec.session_id
                        )
                        file_versions.append(v)

            return file_versions
        finally:
            db.close()

    def resolve_version_pair(
        self,
        file_path: str,
        session_id: Optional[str] = None,
        from_event: Optional[int] = None,
        to_event: Optional[int] = None,
        latest: bool = False
    ) -> Tuple[FileVersion, FileVersion]:
        """Resolve the pair of FileVersions (from_version, to_version) to diff."""
        versions = self.get_file_events(file_path, session_id=session_id)

        if not versions:
            if session_id:
                raise ValueError(f"Session '{session_id}' not found or has no events for '{file_path}'.")
            if not os.path.exists(file_path):
                raise ValueError(f"File '{file_path}' not found in event history.")
            raise ValueError(f"No event history found for '{file_path}'.")

        version_map: Dict[int, FileVersion] = {v.event_id: v for v in versions}

        if from_event is not None and from_event not in version_map:
            raise ValueError(f"Event {from_event} not found.")

        if to_event is not None and to_event not in version_map:
            raise ValueError(f"Event {to_event} not found.")

        if from_event is not None and to_event is not None:
            if from_event == to_event:
                raise ValueError("Not enough file versions to generate diff.")
            return version_map[from_event], version_map[to_event]

        if from_event is not None and to_event is None:
            later_versions = [v for v in versions if v.event_id > from_event]
            if not later_versions:
                raise ValueError("Not enough file versions to generate diff.")
            return version_map[from_event], later_versions[0]

        if from_event is None and to_event is not None:
            earlier_versions = [v for v in versions if v.event_id < to_event]
            if earlier_versions:
                return earlier_versions[-1], version_map[to_event]
            else:
                initial = FileVersion(
                    event_id=0,
                    file_path=file_path,
                    content="",
                    timestamp=version_map[to_event].timestamp,
                    session_id=version_map[to_event].session_id
                )
                return initial, version_map[to_event]

        if len(versions) < 2:
            raise ValueError("Not enough file versions to generate diff.")

        return versions[-2], versions[-1]

    def compute_diff(
        self,
        file_path: str,
        session_id: Optional[str] = None,
        from_event: Optional[int] = None,
        to_event: Optional[int] = None,
        latest: bool = False,
        context: int = 3
    ) -> DiffResult:
        """Compute unified diff and line change statistics between resolved file versions."""
        v1, v2 = self.resolve_version_pair(
            file_path=file_path,
            session_id=session_id,
            from_event=from_event,
            to_event=to_event,
            latest=latest
        )

        lines1 = v1.content.splitlines(keepends=True) if v1.content else []
        lines2 = v2.content.splitlines(keepends=True) if v2.content else []

        lines1 = [l if l.endswith('\n') else l + '\n' for l in lines1]
        lines2 = [l if l.endswith('\n') else l + '\n' for l in lines2]

        diff_gen = difflib.unified_diff(
            lines1,
            lines2,
            fromfile=f"Event {v1.event_id}",
            tofile=f"Event {v2.event_id}",
            n=context
        )
        diff_text = "".join(diff_gen)

        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        added_lines = 0
        removed_lines = 0
        modified_lines = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                r = i2 - i1
                a = j2 - j1
                mod = min(r, a)
                modified_lines += mod
                if a > r:
                    added_lines += (a - r)
                elif r > a:
                    removed_lines += (r - a)
            elif tag == 'insert':
                added_lines += (j2 - j1)
            elif tag == 'delete':
                removed_lines += (i2 - i1)

        ts_from = v1.timestamp.isoformat() if v1.timestamp else None
        ts_to = v2.timestamp.isoformat() if v2.timestamp else None
        sess_id = v2.session_id or v1.session_id or session_id

        return DiffResult(
            file=file_path,
            event_from=v1.event_id,
            event_to=v2.event_id,
            session_id=sess_id,
            timestamp_from=ts_from,
            timestamp_to=ts_to,
            added_lines=added_lines,
            removed_lines=removed_lines,
            modified_lines=modified_lines,
            diff=diff_text,
            from_content=v1.content,
            to_content=v2.content
        )

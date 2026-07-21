import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, TypeDecorator
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AwareDateTime(TypeDecorator):
    """
    Ensure datetimes are timezone-aware and stored in UTC.
    """
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo:
                raise TypeError("tz-naive datetime objects are not allowed.")
            return value.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value

class WorkspaceModel(Base):
    __tablename__ = "workspaces"
    project_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    root_path = Column(String, nullable=False)
    repository = Column(String)
    owner = Column(String)
    client = Column(String)
    environment = Column(String)
    framework = Column(String)
    languages = Column(JSON)
    created_at = Column(AwareDateTime)
    updated_at = Column(AwareDateTime)
    status = Column(String)
    configuration_version = Column(String)
    privacy_mode = Column(String)

class SessionModel(Base):
    __tablename__ = "sessions"
    session_id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("workspaces.project_id"), nullable=False)
    start_ts = Column(AwareDateTime, nullable=False)
    end_ts = Column(AwareDateTime)
    duration_seconds = Column(Integer)
    project_path = Column(String, nullable=False)
    working_directory = Column(String, nullable=False)
    git_repository = Column(String)
    branch = Column(String)
    starting_commit = Column(String)
    ending_commit = Column(String)
    connector = Column(String)
    ai_tool = Column(String)
    model = Column(String)
    user = Column(String)
    status = Column(String)
    event_counts = Column(JSON)
    config_snapshot = Column(JSON)
    warnings = Column(JSON)
    confidence = Column(Float)

class FilesystemEventModel(Base):
    __tablename__ = "filesystem_events"
    event_id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    project_id = Column(String, ForeignKey("workspaces.project_id"), nullable=False)
    timestamp = Column(AwareDateTime, nullable=False)
    path = Column(String, nullable=False)
    normalized_relative_path = Column(String, nullable=False)
    operation = Column(String, nullable=False)
    old_path = Column(String)
    new_path = Column(String)
    size = Column(Integer)
    language = Column(String)
    file_hash = Column(String)
    source = Column(String)
    confidence = Column(Float)
    redaction_state = Column(String)

class GitEventModel(Base):
    __tablename__ = "git_events"
    event_id = Column(String, primary_key=True)
    repository = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    commit_id = Column(String, nullable=False)
    parent_commits = Column(JSON)
    author = Column(String)
    committer = Column(String)
    message = Column(String)
    timestamp = Column(AwareDateTime, nullable=False)
    changed_files = Column(JSON)
    insertions = Column(Integer)
    deletions = Column(Integer)
    diff_metadata = Column(JSON)
    merge_flag = Column(Boolean)
    tag = Column(String)
    session_relation = Column(String)
    source = Column(String)

class TimelineEventModel(Base):
    __tablename__ = "timeline_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    normalized_event_type = Column(String, nullable=False)
    timestamp = Column(AwareDateTime, nullable=False)
    sequence = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    actor_tool = Column(String)
    session_id = Column(String)
    related_event_ids = Column(JSON)
    summary = Column(String)
    details_access_level = Column(String)
    confidence = Column(Float)
    analysis_version = Column(String)

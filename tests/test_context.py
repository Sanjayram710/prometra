import pytest
import os
from prometra.storage.sqlite import SQLiteStorage
from prometra.context.builder import ContextBuilder

def test_context_builder():
    db_path = "/tmp/prometra_test_ctx.db"
    # Ensure directory exists on Windows
    os.makedirs("/tmp", exist_ok=True)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass
            
    storage = SQLiteStorage(db_path)
    builder = ContextBuilder(storage)
    
    # Should build empty context without crashing
    ctx = builder.build_context(project_id="test_proj", project_path="/tmp")
    
    assert ctx.context_id is not None
    assert ctx.project_state.repo.project_id == "test_proj"
    assert ctx.project_state.session is None
    
    storage.engine.dispose()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass

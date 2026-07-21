from prometra.core.schemas import Workspace, Session

def test_workspace_creation():
    ws = Workspace(project_id="test1", name="Test Project", root_path="/tmp")
    assert ws.project_id == "test1"
    assert ws.name == "Test Project"
    assert ws.environment == "development"

def test_session_creation():
    sess = Session(session_id="s1", project_id="test1", project_path="/tmp", working_directory="/tmp")
    assert sess.session_id == "s1"
    assert sess.project_id == "test1"
    assert sess.status == "active"

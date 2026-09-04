"""Tests for session deletion functionality in persistence layer and API."""
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from main import app
from skills import supabase_persistence as db


def test_delete_session_persistence_cascade():
    """Test db.delete_session issues delete calls for all related tables."""
    mock_client = MagicMock()
    
    # Mock table delete chain
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.in_.return_value = mock_table
    
    # Mock execute returns matching code execution order:
    mock_table.execute.side_effect = [
        MagicMock(data=[]),                  # 1. unlinking learning_path_items
        MagicMock(data=[{"id": "seg-1"}]),  # 2. select segments for checkpoints
        MagicMock(data=[]),                  # 3. delete question_checkpoints
        MagicMock(data=[]),                  # 4. delete lesson_segments
        MagicMock(data=[]),                  # 5. delete assessment_reports
        MagicMock(data=[]),                  # 6. delete agent_run_logs
        MagicMock(data=[{"id": "sess-123"}]), # 7. delete session
    ]


    with patch("skills.supabase_persistence.get_client", return_value=mock_client):
        deleted = db.delete_session("sess-123")
        assert deleted is True


def test_delete_session_api_endpoint():
    """Test DELETE /api/v1/sessions/{session_id} route."""
    client = TestClient(app)

    # 1. Non-existent session -> 404
    with patch("skills.supabase_persistence.get_session", return_value=None):
        resp = client.delete("/api/v1/sessions/non-existent-id")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Session not found"

    # 2. Existing session -> 200 OK with success payload
    fake_session = {
        "id": "test-session-uuid",
        "student_id": "00000000-0000-0000-0000-000000000001",
        "topic": "Photosynthesis",
        "level": "beginner",
        "language": "en",
        "time_budget_minutes": 15,
        "status": "completed",
    }
    with patch("skills.supabase_persistence.get_session", return_value=fake_session), \
         patch("skills.supabase_persistence.delete_session", return_value=True):
        resp = client.delete("/api/v1/sessions/test-session-uuid")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["sessionId"] == "test-session-uuid"
        assert "deleted successfully" in data["message"]

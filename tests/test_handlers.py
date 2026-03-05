"""Unit tests for Lambda handlers (run locally with mocked DynamoDB)."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Lambda handlers expect TABLE_NAME; set before import
os.environ.setdefault("TABLE_NAME", "TestTasksTable")

_LAMBDAS = Path(__file__).resolve().parent.parent / "lambdas"


def test_create_task_handler_success():
    """POST /tasks with valid body returns 201 and task with taskId."""
    sys.path.insert(0, str(_LAMBDAS / "create_task"))
    with patch("handler.table") as mock_table:
        from handler import handler

        event = {
            "body": json.dumps({"title": "Test", "description": "D", "status": "pending"}),
            "pathParameters": None,
        }
        result = handler(event, None)
        assert result["statusCode"] == 201
        body = json.loads(result["body"])
        assert "taskId" in body
        assert body["title"] == "Test"
        assert body["description"] == "D"
        assert body["status"] == "pending"
        mock_table.put_item.assert_called_once()


def test_create_task_handler_missing_title():
    """POST /tasks with missing title returns 400."""
    sys.path.insert(0, str(_LAMBDAS / "create_task"))
    from handler import handler

    event = {
        "body": json.dumps({"description": "No title", "status": "pending"}),
        "pathParameters": None,
    }
    result = handler(event, None)
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "title" in body.get("error", "").lower()


def test_create_task_handler_invalid_status():
    """POST /tasks with invalid status returns 400."""
    sys.path.insert(0, str(_LAMBDAS / "create_task"))
    from handler import handler

    event = {
        "body": json.dumps({"title": "Task", "description": "D", "status": "invalid"}),
        "pathParameters": None,
    }
    result = handler(event, None)
    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "status" in body.get("error", "").lower()


def test_get_task_handler_missing_task_id():
    """GET /tasks/{taskId} with missing taskId returns 400."""
    sys.path.insert(0, str(_LAMBDAS / "get_task"))
    from handler import handler

    event = {"body": None, "pathParameters": None}
    result = handler(event, None)
    assert result["statusCode"] == 400


def test_get_task_handler_not_found():
    """GET /tasks/{taskId} when item does not exist returns 404."""
    if "handler" in sys.modules:
        del sys.modules["handler"]
    sys.path.insert(0, str(_LAMBDAS / "get_task"))
    with patch("handler.table") as mock_table:
        mock_table.get_item.return_value = {}
        from handler import handler

        event = {"body": None, "pathParameters": {"taskId": "nonexistent-id"}}
        result = handler(event, None)
        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert "not found" in body.get("error", "").lower()


def test_delete_task_handler_not_found():
    """DELETE /tasks/{taskId} when item does not exist returns 404."""
    if "handler" in sys.modules:
        del sys.modules["handler"]
    sys.path.insert(0, str(_LAMBDAS / "delete_task"))
    with patch("handler.table") as mock_table:
        mock_table.delete_item.return_value = {}
        from handler import handler

        event = {"pathParameters": {"taskId": "nonexistent-id"}}
        result = handler(event, None)
        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert "not found" in body.get("error", "").lower()

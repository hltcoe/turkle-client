import pytest
from unittest.mock import MagicMock

from turkle_client.monitor import BatchMonitor


def test_goal_reached_triggers_callback():
    mock_client = MagicMock()
    mock_progress = {
        "total_tasks": 4,
        "total_task_assignments": 4,
        "total_finished_tasks": 4,
        "total_finished_task_assignments": 4
    }
    mock_client.batches.progress.return_value = mock_progress

    goal_fn = lambda progress: progress['total_finished_tasks'] == progress['total_tasks']
    callback_fn = MagicMock()

    monitor = BatchMonitor(
        client=mock_client,
        batch_id=1,
        goal_fn=goal_fn,
        callback_fn=callback_fn,
        interval=0.1
    )

    monitor.wait(timeout=2)
    callback_fn.assert_called_once()

def test_timeout_raises_error():
    mock_client = MagicMock()
    mock_progress = {
        "total_tasks": 4,
        "total_task_assignments": 4,
        "total_finished_tasks": 0,
        "total_finished_task_assignments": 0
    }
    mock_client.batches.progress.return_value = mock_progress

    goal_fn = lambda progress: progress['total_finished_tasks'] == progress['total_tasks']
    callback_fn = MagicMock()

    monitor = BatchMonitor(
        client=mock_client,
        batch_id=1,
        goal_fn=goal_fn,
        callback_fn=callback_fn,
        interval=0.1
    )

    with pytest.raises(TimeoutError):
        monitor.wait(timeout=0.5)

    callback_fn.assert_not_called()

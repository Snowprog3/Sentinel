from unittest.mock import patch

import pytest

import src.metrics as metrics_module
from src.metrics import REGISTRY, start_metrics_server


@pytest.fixture(autouse=True)
def reset_metrics_server_state():
    metrics_module._metrics_server_started = False
    yield
    metrics_module._metrics_server_started = False


def test_start_metrics_server_skips_when_port_busy():
    with patch("src.metrics.start_http_server", side_effect=OSError("Address already in use")):
        assert start_metrics_server(port=8000) is False


def test_start_metrics_server_starts_once():
    with patch("src.metrics.start_http_server") as mock_start:
        assert start_metrics_server(port=8000) is True
        assert start_metrics_server(port=8000) is True
        mock_start.assert_called_once_with(8000, registry=REGISTRY)

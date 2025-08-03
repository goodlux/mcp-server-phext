"""Basic tests for mcp-server-phext."""

import pytest
from mcp_server_phext import create_server


def test_create_server():
    """Test that server can be created."""
    server = create_server()
    assert server is not None
    assert server.name == "mcp-server-phext"


def test_create_server_with_default_file():
    """Test server creation with default file."""
    server = create_server(default_phext_file="/tmp/test.phext")
    assert server is not None

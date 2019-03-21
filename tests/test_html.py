"""Integration tests for text/html requests."""
import pytest


@pytest.fixture
def headers():
    """Return headers for application/json requests."""
    return {
        "Accept": "text/html",
    }

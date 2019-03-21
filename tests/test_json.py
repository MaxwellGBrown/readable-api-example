"""Integration tests for applicaiton/json requests."""
import pytest


@pytest.fixture
def headers():
    """Return headers for application/json requests."""
    return {
        "Accept": "application/json",
    }

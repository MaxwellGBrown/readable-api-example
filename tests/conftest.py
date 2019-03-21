"""Shared pytest fixtures."""
import pytest
import webtest

from readable_api import ConfigBuilder
from readable_api.resources.base import Resource


@pytest.fixture
def config():
    """Return a pyramid configurator."""
    # TODO Make a fake resource tree from fixtures and implement it here
    #      instead of the shitty app
    builder = ConfigBuilder()
    builder.set_views()

    return builder.config


@pytest.fixture
def app(config):
    """Return a TestApp wrapping a WSGI app."""
    config.set_root_factory(TestRootFactory)

    app = config.make_wsgi_app()
    return webtest.TestApp(app)


class TestRootFactory(Resource):
    """Static resource for the resource tree."""

    __name__ = None
    __parent__ = None

    def __init__(self, request):
        """Instantiate with Request."""
        self.request = request

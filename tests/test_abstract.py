"""Assert the response bodies of text/html & application/json match."""
import json
from unittest import mock

import pytest
import webtest

from readable_api.resources import abstract


def loads_json_from_html_response(html_response):
    """Read the embedded JSON from an HTML response."""
    html_json_body = html_response.html.find(id="response-body").get_text()
    return json.loads(html_json_body)


@pytest.mark.parametrize("accept,accessor", [
    ("application/json", lambda r: json.loads(r.body)),
    ("text/html", loads_json_from_html_response),
])
def test_abstract_resource_tree_makes_leaf_resources(config, accept, accessor):
    """Assert constructed abstract resource trees work."""
    # -------------------------------------------------------------------------
    root_factory = None
    # -------------------------------------------------------------------------

    config.set_root_factory(root_factory)
    wsgi = config.make_wsgi_app()
    app = webtest.TestApp(wsgi)

    response = app.get("/", headers={"Accept": accept})
    data = accessor(response)
    expected_data = {
        # TODO
    }
    assert response.status == '200 OK'
    assert data == expected_data

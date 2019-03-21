"""Assert the response bodies of text/html & application/json match."""
import json
from unittest import mock

import pytest
import webtest

from readable_api.resources import base


def loads_json_from_html_response(html_response):
    """Read the embedded JSON from an HTML response."""
    html_json_body = html_response.html.find(id="response-body").get_text()
    return json.loads(html_json_body)


@pytest.mark.parametrize("route", ["/"])
def test_response_bodies_match(app, route):
    """Assert the json in text/html responses match application/json."""
    json_response = app.get(route, headers={"Accept": "application/json"})
    html_response = app.get(route, headers={"Accept": "text/html"})

    html_json_body = html_response.html.find(id="response-body").get_text()

    # json.loads for comparison to clear whitespace from HTML response
    # and for better output
    assert json.loads(json_response.body) == json.loads(html_json_body)


@pytest.mark.parametrize("accept,status", [
    (None, "200 OK"),
    ("*/*", "200 OK"),
    ("text/html", "200 OK"),
    ("application/json", "200 OK"),
    # TODO
    # ("text/xml", "406 Not Acceptable"),
    # ("text/csv", "406 Not Acceptable"),
])
def test_handle_accept_headers(app, accept, status):
    """Assert response codes depending on Accept header."""
    # TODO It'd be _really_ cool if you could include other sub-rederers
    #      (e.g. csv, xml) to also allow Accept headers for.
    #      Then the HTML response could show ALL of the different rendered
    #      responses for each type in like tabs or something.
    headers = {"Accept": accept} if accept else {}
    response = app.get("/", headers=headers)
    assert response.status == status


@pytest.mark.parametrize("accept,accessor", [
    ("application/json", lambda r: json.loads(r.body)),
    ("text/html", loads_json_from_html_response),
])
@pytest.mark.parametrize("subresource_names", [
    tuple(),
    ("foo",),
    ("likes", "posts", "images"),
])
def test_leaf_resource_shows_sub_resources(config, accept, accessor,
                                           subresource_names):
    """Assert leaf resource displays data."""
    leaf_resource = type("TestLeafResource", (base.LeafResource,),
                         {"resource_map": dict()})
    for name in subresource_names:
        subresource = type("SubResource", (base.Resource,),
                           {"__name__": name})
        leaf_resource.register(name)(subresource)

    config.set_root_factory(leaf_resource)
    wsgi = config.make_wsgi_app()
    app = webtest.TestApp(wsgi)

    response = app.get("/", headers={"Accept": accept})
    data = accessor(response)
    expected_data = {
        "resources": {
            name: {"url": f"http://localhost/{name}/"}
            for name in subresource_names
        }
    }
    assert response.status == '200 OK'
    assert data == expected_data


# NOTE Abandoned here for the abstract stuff
# @pytest.mark.parametrize("accept,accessor", [
#     ("application/json", lambda r: json.loads(r.body)),
#     ("text/html", loads_json_from_html_response),
# ])
# def test_container_resource_shows_query_data(accept, accessor, config):
#     """Assert leaf resource displays data."""
#     resource = type(
#         "TestResource",
#         (base.ContainerResource,),
#         {
#             # TODO Needs to be a generic submethod that returns queried
#             #      resources so their data can be accessed.
#             #      But then how is the data given to those resources?
#             #      Like, how does the URL for that subresource get it's data VS
#             #      how the query gets the data?
#             "query": mock.Mock(return_value={
#                 "hello": "world",
#             }),
#         }
#     )
# 
#     config.set_root_factory(resource)
#     wsgi = config.make_wsgi_app()
#     app = webtest.TestApp(wsgi)
# 
#     response = app.get("/", headers={"Accept": accept})
#     data = accessor(response)
#     expected_data = {
#     }
#     assert response.status == '200 OK'
#     assert data == expected_data

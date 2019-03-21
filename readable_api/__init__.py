"""Traversal application that accepts text/html and application/json."""
from pyramid.config import Configurator

from readable_api import views
from readable_api.resources import RootFactory, Resource


class ConfigBuilder:
    """Builder recipe for constructing a pyramid.config.Configurator."""

    def __init__(self, **settings):
        """Instantiate a configurator to build upon."""
        self.config = Configurator(**settings)

    def set_views(self):
        """Add all the views."""
        pyramid_views = [
            {"request_method": "GET", "view": views.GET},
            {"request_method": "POST", "view": views.POST},
            {"request_method": "PUT", "view": views.PUT},
        ]
        content_types = [
            {"accept": "application/json", "renderer": "json"},
            {"accept": "text/html", "renderer": "templates/get.mako"},
        ]

        self.config.include("pyramid_mako")

        # https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/viewconfig.html#accept-header-content-negotiation
        self.config.add_accept_view_order(
            "application/json",
            weighs_more_than="text/html",
        )

        for view in pyramid_views:
            for content_type in content_types:
                kwargs = {"context": Resource, **view, **content_type}

                # NOTE This is a simple and dumb way to make pyramid_mako
                #      use the same exact data as a json renderer.
                #      There has to be a more flexible way, because other
                #      content types or custom renderers might be used.
                #      But for the time being this works.
                if kwargs["accept"] == "text/html":
                    fxn = kwargs.pop("view")
                    kwargs["view"] = _mako_json_to_renderer_wrapper(fxn)

                self.config.add_view(**kwargs)


def build_wsgi(global_config=None, **settings):
    """Return WSGI app to be served."""
    builder = ConfigBuilder(**settings)
    builder.set_views()
    builder.config.set_root_factory(RootFactory)

    app = builder.config.make_wsgi_app()
    return app


def _mako_json_to_renderer_wrapper(view):
    """Wrap route to return data as a key in a dictionary.

    This is done because pyramid_mako takes your returned rendering object and
    muddles it with the top level mako Context.kwargs.

    That specifically ruins the use case where we can take the same exact data
    we're rendering to JSON and render it in a <pre> in an html template; we
    have no prior knowledge of the structure of the JSON object being rendered,
    and nor should we by the template point.
    """
    def _new_view(*args):
        return {"data": view(*args)}
    return _new_view

"""Pyramid view callables."""
import json


def GET(context, request):
    """Return raw API response data associated with request context.

    This generic view only changes functionality based on the view
    implementation.
    """
    print(f"GET context: {context.__name__}")
    return context.data


def POST(context, request):
    """Create/update an object based on the payload or whatever."""
    # TODO is context.post() really what we want to use?
    if not getattr(context, "post", None):
        request.response.status_int = 405
        return {}

    try:
        # TODO MultiDict -> dict loses "array" data that might exist
        result_url = context.post(dict(request.POST))
    except ValueError:  # TODO Make a validation error or some shit idk
        request.response.status_int = 400
        return {}

    # TODO You're supposed to really highlight the URL & resource that you
    #      just created in the response but right now it just shows the listing
    #      again. How do you do a 201 Created, but also direct somebody either
    #      to the new URL (that they would have done a PUT against) or
    #      highlight the resource they just would have created on your listing?
    #      Do you add something to the response?
    request.response.status_int = 201
    request.response.headers["Location"] = result_url
    return context.data


def PUT(context, request):
    """Perform an upsert on the resource given some request data."""
    # TODO <form method="PUT"> DOESN'T WORK
    #      THERE NEEDS TO BE AJAX FUCK ME
    try:
        request_body = json.loads(request.body)
        context.put(request_body)
    except ValueError:
        return {}

    # TODO How do we know if it was created or updated
    return context.data

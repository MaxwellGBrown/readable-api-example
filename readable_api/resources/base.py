"""Pyramid Resource Tree objects to define API paths.

NOTE That there are two types of resources:
    One that describes only children (e.g. Posts will only ever have posts)
    One that describes sub-resources (e.g. A User will have Posts, Likes, etc.)

There are still a lot of unanswered questions as to what the
similarities/differences these two types of resources share.

For example:
  - Do they share the same standard output structure?
    Like, do they both just have "results"? Do they both have pagination?
  - Is there associated metadata with resources that have sub-apis?

    I guess the answer is Yes: a User should have a Username & Email for
    example, which is associated to the user & can be updated.
    But also, there are sub-resources to that user

Remember to think in URL Path(s) because that's what this is really defining.

/Users/1/Likes/1 - Accessing a users Likes
/Users/1/1 - Accessing the 1st item for User w/ id of 1?
"""
import jsonschema


def resource_tree_builder(root_item):
    """Return a root_factory implementing a resource tree based off item."""


class Resource:
    """Base class of all Resource Tree resources.

    This is used to make it so that if None is returned a 404 happens.
    """

    __name__ = None
    __parent__ = None
    __acl__ = tuple()

    _request = None

    @property
    def request(self):
        """Ask parent resource for request until the RootFactory is reached."""
        if self.__parent__:
            return self.__parent__.request
        else:
            return self._request

    @request.setter
    def request(self, value):
        """Set the most parental request. Only be used by RootFactory."""
        if self.__parent__:
            self.__parent__.request = value
        else:
            self._request = value

    def __getitem__(self, key):
        """Return any child elements associated with sub-path part, key."""
        return None

    def set_parent(self, parent):
        """Set the parent resource for this element for URL creation."""
        self.__parent__ = parent

    @property
    def data(self):
        """Return raw API response data."""
        return {
            "schema": self.schema,
            "results": [
                # TODO How to send query params from querystring &/or POST body
                # TODO self.query or self.subresources?
                # r.data for r in self.query(**self.request.data)
            ]
        }

    @property
    def schema(self):
        """Return the JSON Schema of this Resource."""
        return {
            "$schema": "http://json-schema.org/schema#",
            "$id": f"{self.request.resource_url(self)}#schema",
            # Below are standard metadata fields for JSON Schema
            # "title": "",
            # "description": "",
            # "default": "",
            # "examples": [...],
        }

    def validate(self, data):
        """Validate data against self.schema."""
        try:
            jsonschema.validate(self.schema, data)
        except jsonschema.exceptions.ValidationError:
            raise ValueError("DIDN'T VALIDATE JSON SCHEMA")


class LeafResource(Resource):
    """Resource that represents a single item; may have sub-resources."""

    resource_map = dict()

    @classmethod
    def register(cls, name):
        """Register a sub-resource."""
        def _register(sub_cls):
            cls.resource_map[name] = sub_cls
            return sub_cls

        return _register

    @classmethod
    def get(cls, name):
        """Return an instantiated LeafResource using the name as id."""
        raise NotImplementedError()

    @property
    def subresources(self):
        """Return instantiated subresources of this Resource."""
        subresources = dict()
        for name, cls in self.resource_map.items():
            sub_resource = cls()  # TODO instantiate with...?
            sub_resource.set_parent(self)
            subresources[name] = sub_resource
        return subresources

    @property
    def data(self):
        """Return raw API response data in a hypermedia format."""
        return {
            "resources": {
                name: {
                    # TODO What other "metadata" cana sub resource have?
                    "url": self.request.resource_url(subresource)
                }
                for name, subresource in self.subresources.items()
            },
        }

    # def __init__(self, name=None):
    #     """Init with the path name associated with this resource."""
    #     self.__name__ = name

    def __init__(self, request=None, parent=None, name=None):
        """Init with the resource tree stuff.

        Resource.request is a parent-climbing thing for request so only set
        that in certain scenarios.
        """
        if request:
            self.request = request
        self.__name__ = name

    def __getitem__(self, key):
        """Return subresource located at key."""
        return self.subresources.get(key)


class RootFactory(LeafResource):
    """Top level resource for traversal."""

    __name__ = None
    __parent__ = None

    def __init__(self, request):
        """Instantiate with request."""
        self.request = request

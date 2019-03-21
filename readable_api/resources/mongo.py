"""Example of MongoDB resources."""
import pymongo

from readable_api.resources.base import LeafResource, Resource, RootFactory


mongo = pymongo.MongoClient('mongo', port=27017)


@RootFactory.register("foo")
class Foo(Resource):
    """Subresource of 'Foos'."""

    __name__ = "foo"

    page_size = 5

    @property
    def schema(self):
        """Return the JSON Schema for a Foo resource."""
        # TODO The schema of a container resource...
        #      This is the same as the leaf.
        #      However, this isn't actually the schema of the response
        return {
            "$id": f"{self.request.resource_url(self)}#schema",
            "type": "object",
            "properties": {
                "foo": {"type": "string"},
                # generated fields shouldn't be submitted or in forms
                "url": {"type": "string", "generated": True},
            }
        }

    @property
    def data(self):
        """Return raw API response data in a hypermedia format."""
        previous_url = None
        page = int(self.request.GET.get('page', 1))
        next_url = self.request.resource_url(self, query={"page": page + 1})
        pagination = (page - 1) * self.page_size

        count = mongo['readable-api'].foo.count()

        if page > 1:
            previous_url = self.request.resource_url(
                self,
                query={"page": page - 1},
            )
        if (self.page_size * page) >= count:
            next_url = None

        results = [
            r for r in
            mongo['readable-api'].foo.find(
                limit=self.page_size,
                skip=pagination,
            )
        ]

        return {
            "count": count,
            "next": next_url,
            "previous": previous_url,
            "results": [
                {
                    "url": self.request.resource_url(
                        self.make_child(result['foo'])
                    ),
                    **result
                }
                for result in results
            ],
            "schema": self.schema,
        }

    def make_child(self, key):
        """Birth a child resource."""
        child = Bar(key)
        child.__parent__ = self
        return child

    # def __init__(self, parent):
    #     """Instantiate Resource manager with the request."""
    #     self.__parent__ = parent

    #     self.request = parent.request

    def __getitem__(self, key):
        """Return subresources of this resource."""
        result = mongo['readable-api'].foo.find_one({"foo": key})
        if result:
            return self.make_child(key)
        return None

    def post(self, data):
        """Upsert data as a resource or whatever."""
        self.validate(data)

        mongo['readable-api'].foo.insert_one(data)

        return self.request.resource_url(self.make_child(data['foo']))


class Bar(LeafResource):
    """Subresource of 'Foo'."""

    @property
    def schema(self):
        """Return the JSON Schema for a Foo resource."""
        # NOTE This is exactly the same as the other thing.
        return {
            "$id": f"{self.request.resource_url(self)}#schema",
            "type": "object",
            "properties": {
                "foo": {"type": "string"},
                # generated fields shouldn't be submitted or in forms
                "url": {"type": "string", "generated": True},
            }
        }

    @property
    def data(self):
        """Return Data associated with Bar."""
        return {  # TODO Actually query for this shit
            "foo": self.__name__,
            "url": f"{self.request.resource_url(self)}",
        }

    def __init__(self, a):
        """Instantiate Bar with a value."""
        self.__name__ = a

    def put(self, data):
        """Upsert data associated to this resource."""
        self.validate(data)

        mongo['readable-api'].foo.update(
            {"foo": self.data["foo"]},
            data,
        )

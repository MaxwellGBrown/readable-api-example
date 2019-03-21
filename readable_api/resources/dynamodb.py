"""Example of DynamoDB resources."""
import boto3

from readable_api.resources.base import LeafResource, Resource, RootFactory


dynamo = boto3.client("dynamodb")


class Product(LeafResource):
    """A single DynamoDB record."""

    __parent__ = None
    __name__ = None

    @property
    def schema(self):
        """Return jsonschema associated with product API responses."""
        return {
            "$id": f"{self.request.resource_url(self)}#schema",
            "type": "object",
            "properties": {
                # NOTE Wait a second. This is the same as Products.schema
                #      Is this a bad thing? Am I doing something wrong?
                #
                #      This URL needs to exist so that this resource can be
                #      updated/deleted after creation.
                #
                #      Also, you don't want to have to query for this resource
                #      every time you want to read it... right?
                "ProductId": {"type": "string"},
                "sku": {"type": "string"},
                "color": {"type": "string"},
                "cost_to_manufacture": {"type": "string"},
                # generated fields shouldn't be submitted or in forms
                "url": {"type": "string", "generated": True},
            },
        }

    def __init__(self, dynamodb_record):
        """Instantiate with a record or whatever."""
        self.record = dynamodb_record
        self.__name__ = dynamodb_record["ProductId"]["S"]

    @property
    def data(self):
        """Return."""
        return self.__parent__._dynamo_to_record(self.record)


@RootFactory.register('products')
class Products(Resource):
    """Demonstration of DynamoDB products."""

    __name__ = "products"

    @property
    def schema(self):
        """Return jsonschema associated with product API responses."""
        return {
            "$id": f"{self.request.resource_url(self)}#schema",
            "type": "object",
            "properties": {
                "ProductId": {"type": "string"},
                "sku": {"type": "string"},
                "color": {"type": "string"},
                "cost_to_manufacture": {"type": "string"},
                # generated fields shouldn't be submitted or in forms
                "url": {"type": "string", "generated": True},
            }
        }

    kwargs = {
        "TableName": "Testing",
        "Limit": 5,  # aka page_size
    }

    @staticmethod
    def _get_count(client, **kwargs):
        # NOTE To get the count of a dynamo query/scan, YOU MUST PAGINATE
        #      THROUGH ALL RESPONSES WHILE THE READS ARE >1MB!
        #      This effectively means you're paginating through the whole
        #      table just to count the items before returning a subset of that
        #      as a paginated response.
        #      AKA THIS MAY BE EXPENSIVE AS SHIT AND MIGHT NOT BE WORTH IT
        number_of_requests_just_to_count = 1
        count = 0
        # TODO Use query if the user is querying.
        kwargs = dict(kwargs)
        kwargs.pop('ExclusiveStartKey', None)
        kwargs.pop('Limit', None)
        kwargs["Select"] = "COUNT"
        response = client.scan(**kwargs)
        count += response["Count"]
        while response.get('LastEvaluatedKey'):
            kwargs['ExclusiveStartKey'] = response.get("LastEvaluatedKey")
            response = client.scan(**kwargs)
            count += response["Count"]
            number_of_requests_just_to_count += 1

        print(f"It took {number_of_requests_just_to_count} requests "
              "just to return the count of this resource.")
        return count

    def _make_child(self, record):
        child = Product(record)
        child.set_parent(self)
        return child

    @property
    def data(self):
        """Return raw API response data in a hypermedia format."""
        kwargs = dict(self.kwargs)
        if self.request.GET.get('pagination'):
            kwargs['ExclusiveStartKey'] = {
                "ProductId": {"S": self.request.GET['pagination']},
            }
        # TODO Scan used when no query, query used when query.
        response = dynamo.scan(Select="ALL_ATTRIBUTES", **kwargs)

        next_url = None
        if response['LastEvaluatedKey']:
            next_url = self.request.resource_url(
                self,
                query={"pagination": response["LastEvaluatedKey"]["ProductId"]["S"]},  # noqa
            )

        return {
            # "count": self._get_count(dynamo, **kwargs),
            # TODO How can we track the last ExclusiveStartKey used?
            # "previous": previous_url,
            "next": next_url,
            "results": [self._dynamo_to_record(r) for r in response.get("Items", [])],  # noqa
            "schema": self.schema,
        }

    def _dynamo_to_record(self, record):
        """Return a normal record when given a dynamo record."""
        empty = {"S": None}
        return {
            "url": self.request.resource_url(self._make_child(record)),
            "ProductId": record['ProductId']['S'],
            "sku": record.get('sku', empty)['S'],
            "color": record.get('color', empty)['S'],
            "cost_to_manufacture": record.get('cost_to_manufacture', empty)['S'],  # noqa
        }

    # def __init__(self, parent):
    #     """Instantiate Resource w/ request."""
    #     self.__parent__ = parent

    def __getitem__(self, key):
        """Query for the sub-product and return Product()."""
        # TODO Currently, this is running a query every god damn time we are
        #      building or validating a URL.
        response = dynamo.query(
            Select="ALL_ATTRIBUTES",
            KeyConditionExpression=f"ProductId = :productId",
            ExpressionAttributeValues={":productId": {"S": key}},
            **self.kwargs,
        )
        print(response)
        if response["Items"]:
            child = self._make_child(response["Items"][0])
            print('child', child)
            return child
        return None

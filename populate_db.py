"""Populate the mongodb with data to be used in the webapp."""
import pymongo


def main():
    """Clear & re-import test data."""
    client = pymongo.MongoClient('localhost', 27018)
    db = client['readable-api']

    db.foo.drop()

    db.foo.insert_one({'foo': 'bar'})
    db.foo.insert_one({'foo': 'baz'})
    db.foo.insert_one({'foo': 'qux'})
    db.foo.insert_one({'foo': 'xyz'})
    db.foo.insert_one({'foo': 'schoop'})
    db.foo.insert_one({'foo': 'woop'})


if __name__ == "__main__":
    main()

"""package utils."""
import csv
import json

try:
    # Python 2
    from io import StringIO as DummyFile
except ImportError:
    # Python 3
    from io import BytesIO as DummyFile

from elasticsearch.connection import create_ssl_context
from elasticsearch import Elasticsearch


def to_csv(data):
    """Get a list of dictionaries and return as a csv string."""
    if not data or not isinstance(data, list):
        return ""

    # You got a better way to do this section? PR me please.
    dummy = DummyFile()
    fieldnames = list(data[0].keys())
    writer = csv.DictWriter(
        dummy,
        fieldnames=fieldnames,
        quoting=csv.QUOTE_NONNUMERIC,
        lineterminator='\n'
    )
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return dummy.getvalue()


def read_as_json(filename):
    """Get a filepath of a json file and return a list of dicts."""
    with open(filename, 'r') as file:
        return json.loads(file.read())


def execute_query(query, hosts_list, user=None, password=None, ca_filepath=None):
    """Helper function to perform a query to ES."""
    auth = (user, password,) if user and password else None
    # Create SSL Certificate context, if needed.
    ssl_context = create_ssl_context(cafile=ca_filepath) if ca_filepath else None

    es = Elasticsearch(hosts_list, http_auth=auth, ssl_context=ssl_context)
    return es.search(query)

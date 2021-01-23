"""package utils."""
import json

from elasticsearch.connection import create_ssl_context
from elasticsearch import Elasticsearch


def pluralize(word, override):
    """Helper to get word in plural form."""
    if word in override:
        return override[word]
    return word + 'es' if word[-1] == 's' else word + 's'


def to_csv(data):
    """Get a list of dictionaries and return as a csv string."""
    if not data or not isinstance(data, list):
        return ""

    # You got a better way to do this section? PR me please.
    result = str()
    header = list(data[0].keys())
    result += '"' + '","'.join(header) + '"\n'

    for element in data:
        row = str()
        for key in header:
            value = element[key]
            if isinstance(value, int) or isinstance(value, float):
                row += '{},'.format(value)
            elif isinstance(value, list):
                row += '"' + ','.join(value) + '",'
            else:
                row += '"{}",'.format(value)
        result += row[:-1] + '\n'
    return result


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

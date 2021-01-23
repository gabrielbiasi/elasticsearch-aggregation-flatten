"""Aggregation Flatten in standalone mode."""
import json
import sys
import configparser

from aggregation_flatten import AggregationFlatten
from aggregation_flatten.utils import execute_query, read_as_json


CONFIG = configparser.ConfigParser()
CONFIG.read(sys.argv[1])

if CONFIG.getboolean('test', 'enabled', fallback=False):
    # In test mode, we use raw query and response files.
    query = read_as_json(CONFIG.get('test', 'query'))
    response = read_as_json(CONFIG.get('test', 'response'))
else:
    # Perform the query and get the results.
    query = read_as_json(sys.argv[2])
    response = execute_query(
        query,
        hosts_list=CONFIG.get('elastic', 'hosts').split(','),
        user = CONFIG.get('elastic', 'user'),
        password = CONFIG.get('elastic', 'password'),
        ca_filepath = CONFIG.get('elastic', 'ca_filepath'),
    )

# Process both query and response in order
# to flat the results of the aggregation.
result = AggregationFlatten(
    query,
    response,
    flat_top_hits = CONFIG.getboolean('misc', 'flat_top_hits', fallback=True),
    plural_top_hits = CONFIG.getboolean('misc', 'plural_top_hits', fallback=True),
    plurals = json.loads(CONFIG.get('misc', 'plurals', fallback='{}')),
    date_format = CONFIG.get('misc', 'date_format', fallback=None),
    timezone = CONFIG.get('misc', 'timezone', fallback=None),
    remove_keyword = CONFIG.getboolean('misc', 'remove_keyword', fallback=True),
).render(CONFIG.get('misc', 'output_mode', fallback='json'))

sys.stdout.write(result)
sys.exit(0)

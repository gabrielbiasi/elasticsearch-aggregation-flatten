"""Aggregation Flatter in execution mode."""
import sys
import configparser

from aggregation_flatter import AggregationFlatter
from aggregation_flatter.utils import execute_query, read_as_json


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
result = AggregationFlatter(
    query,
    response,
    flat_one_hit = CONFIG.getboolean('misc', 'flat_one_hit', fallback=True),
    plural_hits = CONFIG.getboolean('misc', 'plural_hits', fallback=True),
    remove_keyword = CONFIG.getboolean('misc', 'remove_keyword', fallback=True),
    output_mode = CONFIG.get('misc', 'output_mode', fallback='json')
).render()

sys.stdout.write(result)
sys.exit(0)

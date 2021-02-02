"""core."""
import json
import pytz
import sys
import uuid

from datetime import datetime
from .utils import pluralize, to_csv

ISO8601 = "%Y-%m-%dT%H:%M:%S.%fZ"


class AggregationFlatten(object):
    """..."""
    OUTPUT_MODES = ['json', 'pretty_json', 'csv']
    AGGREGATIONS = ['terms', 'sum', 'avg', 'min', 'max', 'cardinality']
    UNKNOWN_FIELD_PREFIX = 'unknown-field-'

    def __init__(self, query, response, flat_top_hits=True, plural_top_hits=True, plurals=None, date_format=None, timezone=None, remove_keyword=True):
        self.query = query
        self.response = response
        self.flat_top_hits = flat_top_hits
        self.plural_top_hits = plural_top_hits
        self.plurals = plurals or dict()
        self.date_format = date_format
        self.timezone = timezone
        self.remove_keyword = remove_keyword

    def process_date(self, value):
        """Helper to sanitize date values."""
        if not isinstance(value, str):
            return value
        try:
            date = datetime.strptime(value, ISO8601)
            if self.timezone:
                date = (date
                        .replace(tzinfo=pytz.utc)
                        .astimezone(pytz.timezone(self.timezone)))
            value = date.strftime(self.date_format or ISO8601)
        except ValueError:
            pass
        return value

    def process_field(self, agg_path):
        """Getting the name of the field, based on the original query."""
        current_path = self.query
        for agg in agg_path.split('|'):
            current_path = current_path['aggs'][agg]

        if 'top_hits' in current_path:
            return current_path['top_hits']['_source'], current_path['top_hits']['size']

        # Common aggregation formats
        for agg_type in self.AGGREGATIONS:
            if agg_type in current_path:
                return current_path[agg_type]['field'], 0

        # Fallback to a default field name
        return self.UNKNOWN_FIELD_PREFIX + str(uuid.uuid4())[:8]

    def process_data(self, subdata, agg_path):
        """Normalize the data of the bucket."""
        data = None
        field_name, size = self.process_field(agg_path)

        if 'hits' in subdata.keys():  # top hits
            data = []
            for hits in subdata['hits']['hits']:
                if 'fields' in hits:  # keyword field
                    raw = hits['fields'][field_name][0]
                else:  # text field
                    raw = hits['_source'][field_name]
                data.append(self.process_date(raw))

            if self.flat_top_hits and size == 1 and len(data) == 1:
                data = data[0]
            elif self.plural_top_hits and size > 1:
                field_name = pluralize(field_name, self.plurals)

        else:  # count, avg, max, min, sum, terms
            for common in ['value_as_string', 'key', 'value']:
                if common in subdata.keys():
                    data = self.process_date(subdata[common])
                    break

        # Remove ".keyword" from field name, if needed.
        if self.remove_keyword and '.keyword' in field_name:
            field_name = field_name.replace('.keyword', '')

        return {field_name: data} if data else {}

    def process_bucket(self, data, agg_path):
        """Here the magic happens.
        This recursive function checks for any numeric keys in the current dict
        (because Kibana does that).
        For every new inner bucket found, we recursively process it, and after
        that we look for specific data fields, using 'process_data'. We only
        consider to process the current bucket if any data was found in the
        inner buckets. We also preserve the counter of the deepest bucket."""
        row = {}
        # Processing the data within inner buckets.
        children_aggregations = [key for key in data.keys() if key.isnumeric()]
        for aggr in children_aggregations:
            if 'buckets' in data[aggr]:
                if not data[aggr]['buckets']:
                    # Empty bucket found!
                    return {}
                for bucket in data[aggr]['buckets']:
                    # Recursively process data of inner buckets.
                    row.update(
                        self.process_bucket(bucket, agg_path + '|' + aggr)
                    )

                # If the children aggretations has inner aggregations within
                # but no data really came, so probally this current bucket
                # does not meet an 'min_doc_count' rule. So we also ignore
                # this whole bucket aswell.
                if not row:
                    return {}

            # Processing data, probably with our data.
            row.update(self.process_data(data[aggr], agg_path + '|'  + aggr))

        row.update(self.process_data(data, agg_path))
        # Ensure the deepest doc count for every bucket.
        if 'doc_count' not in row:
            row['doc_count'] = data['doc_count']
        return row

    def process_query(self):
        """Consider the first agregation available
        as the main aggregation to be processed."""
        base = list(self.response['aggregations'].keys())[0]
        bucket_list = self.response['aggregations'][base]['buckets']

        results = []
        for bucket in bucket_list:
            # The function 'process_bucket' might return an empty dict
            # if does not has data until the lastest bucket available.
            # Here, we filter out these cases.
            data = self.process_bucket(bucket, base)
            if data:
                results.append(data)
        return results

    def render(self, output_mode=None):
        """..."""
        mode = output_mode if output_mode in self.OUTPUT_MODES else self.OUTPUT_MODES[0]
        results = self.process_query()

        if mode == 'json':
            return json.dumps(results, separators=(',', ':'))
        elif mode == 'pretty_json':
            return json.dumps(results, indent=2)
        else:
            return to_csv(results)

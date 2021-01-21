# elasticsearch-aggregation-flatten
This python package helps to process an aggregation response from Elasticsearch and output it in a ready -to-use format, such as json and csv.

## The Problem
Elasticsearch is a amazing tool to perform almost any type of bucket and metric aggregations, but the Query DSL and the response provided by the API server is rather over complicated to work with.

This problem scales up when multiple bucket aggragations are combined. For example, consider the following Query DSL with multiple bucket aggregations:
```json
{
  "size": 0,
  "aggs": {
    "2": {
      "terms": {
        ...
      },
      "aggs": {
        "3": {
          "terms": {
            ...
          },
          "aggs": {
            "4": {
              "terms": {
                "min_doc_count": 2,
                ...
              },
              "aggs": {
                "5": {
                  "top_hits": {
                    ...
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "query": {...}
}
```
This multiple bucket aggregation will return a response with the following format:

```json
{
  "took": 100,
  "timed_out": false,
  "_shards": {
    ...
  },
  "hits": {
    "hits": [],
    ...
  },
  "aggregations": {
    "2": {
      "key": "term1",
      "doc_count": 2,
      "buckets": [
        {
          "3": {
            "key": "term2",
            "doc_count": 2,
            "buckets": [
              {
                "4": {
                  "key": "term3",
                  "doc_count": 2,
                  "buckets": [
                    {
                      "5": {
                        "hits": {
                          "total": {...},
                          "hits": [
                            {...},
                            ...
                          ]
                        }
                      }
                    }
                  ]
                }
              }
            ]
          }
        }
      ]
    }
  }
}
```

The data is spread across all buckets, in a way that is difficult to work with. If you want to organize the data of each inner bucket with its parent buckets, you will need to do a treatment to flatten them into the same document.

## The Solution
The class `AggregationFlatten` makes this job a lot easier. All you have to do is to create a new instance of this class, passing as parameters the original query DSL and the response returned by Elasticsearch. After that, just call `process_query()`, to receive the data as a list of dicts.

```python
>>> flatten = AggregationFlatten(query, response)
>>> data = flatten.process_query()
>>> data
[{"field1":"value1","field2":"value2","field3":"value3"}]
>>> type(data)
<class 'list'>
>>> type(data[0])
<class 'dict'>
```


## Output Options
You can also use the method `render()` in order to get all data in a ready-to-use format. The current formats available to render are minified json, pretty json and csv.
```python
>>> flatten = AggregationFlatten(query, response)
>>> data = flatten.render()  # default: minified json
>>> type(data)
<class 'str'>
>>> data
'[{"field1":"value1","field2":"value2","field3":"value3"},{"field1":"value1","field2": "value2","field3":"value3"}]'

# You can call again render() with other parameters.
>>> data = flatten.render('pretty_json')
>>> type(data)
<class 'str'>
>>> data
"""
[
    {
        "field1": "value1",
        "field2": "value2",
        "field3": "value3"
    },
    {
        "field1": "value1",
        "field2": "value2",
        "field3": "value3"
    }
]
"""

>>> data = flatten.render('csv')
>>> type(data)
<class 'str'>
>>> data
"""
"field1","field2","field3"
value1,value2,value3
value1,value2,value3
"""
```

## Standalone Mode
The standalone mode works by reading a configuration file as the first argument in the command line, containing all the data needed to connect and perform the query to a Elasticsearch cluster and other settings. In the second argument, you pass the filepath containing the query DSL in a JSON format.
```bash
~$: python -m aggragation_flatten ./config.ini ./query_file.json
```

The configuration file can be used as following:
```ini
[elastic]
# full URI of the ES clusters (comma separated)
hosts = https://hostname1:9200,https://hostname2:9200,https://hostname3:9200
# Basic auth user
user = my-elastic-user
# Basic auth password
password = my-elastic-password
# Path to a CA certificate file, if needed.
ca_filepath = /path/to/ca/certificate.pem
# Index to perform the query
index = index-pattern-to-aggregate-*

# These are the same keyword arguments offered on AggregationFlatten class.
[misc]
# top hits with size 1 will return as flatted value
flat_one_hit = true
# top hits with multiple hits will append a 's' to the field name
plural_hits = true
# remove the '.keyword' suffix from the name fields
remove_keyword = true
# output format to stdout: json, pretty_json, csv
output_mode = pretty_json

# Test Mode: Don't actually perform the query.
# It just use the files below as inputs.
[test]
enabled = false              # choices: true, false
query = qe1.json            # query file
response = re1.json         # response file
```

## Disclaimer
This is still a WIP project.
Feel free to submit your PR with fixes and suggestions.
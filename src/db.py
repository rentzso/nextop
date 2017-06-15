from elasticsearch import Elasticsearch
import os
host = 'http://{}:{}@localhost:9200/'.format(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASSWORD'])
es = Elasticsearch([host])

def getRecommendations(topics):
    """
    This will generate an elastisearch with a custom scoring script for the input topics.
    For example if we have
    ```
    topics = ['SPORT', 'POLITICS']
    ```
    the query executed will be
    ```
    {
        "query": {
            "function_score": {
                "query": {
                    "match": { "topics": "SPORT POLITICS" }
                },
                "script_score" : {
                    "script" : {
                        "inline": "(_index['topics']['kill'].tf() + _index['topics']['tax_religion'].tf())/Math.max(1, doc['topics'].size())",
                        "lang": "groovy"
                    }
                }
            }
        }
    }
    ```
    """

    # The tf_string computes the term frequency of the query term
    tf_string = """_index['topics']['{}'].tf()"""
    # Sum all the occurences of each topic
    sum_frequencies_script = ' + '.join([
        tf_string.format(topic.lower()) for topic in topics
    ])
    # Normalize by the length of the 'topics' field
    script = """Math.abs(({})/Math.max(1, doc['topics'].size()) - 0.75)""".format(sum_frequencies_script)
    topics = ' '.join(topics)
    # We are creating the query as string (and not as JSON) because
    # the elasticsearch json converter escapes single quotes in the groovy script
    query = """{
        "size": 10,
        "query": {
            "function_score": {
                "query": {
                    "match": { "topics": "%s" }
                },
                "script_score" : {
                    "script" : {
                        "inline": "%s",
                        "lang": "groovy"
                    }
                }
            }
        }
    }""" % (topics, script)
    results = es.search(index="documents", body=query)
    return [result['_source'] for result in results['hits']['hits']]


def getRandomNews(seed):
    query = {
       "size": 1,
       "query": {
          "function_score": {
             "functions": [
                {
                   "random_score": {
                      "seed": seed
                   }
                }
             ]
          }
       }
    }
    results = es.search(index="documents", body=query)
    return results['hits']['hits'][0]['_source']


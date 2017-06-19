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
    should = [
        {"constant_score": {
            "filter" : {
                "match": { "topics" :  topic} }}}
        for topic in topics
    ]
    query = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {"should": should }
                },
                "script_score" : {
                    "script" : {
                        "inline": "- Math.abs(_score/doc[\u0027num_topics\u0027].value - 0.75)"
                    }
                }
            }
        }
    }
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


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
        tf_string.format(topic.lowercase()) for topic in topics
    ])
    # Normalize by the length of the 'topics' field
    script = """({})/Math.max(1, doc['topics'].size())""".format(tf_string)
    topics = ' '.join(topics)
    query = """{
        "query": {
            "function_score": {
                "query": {
                    "match": { "topics": {} }
                },
                "script_score" : {
                    "script" : {
                        "inline": "{}",
                        "lang": "groovy"
                    }
                }
            }
        }
    }""".format(topics, script)
    results = es.search(index="documents", body=query)
    return [result['_source'] for result in results]


def getRandomNews():
    query = {
       "size": 1,
       "query": {
          "function_score": {
             "functions": [
                {
                   "random_score": {
                      "seed": "1477072619038"
                   }
                }
             ]
          }
       }
    }
    results = es.search(index="documents", body=query)
    return results[0]['_source']


from elasticsearch import Elasticsearch
from random import randint
import os

class Queries(object):
    
    def __init__(self):
        hosts = [
            host.format(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASSWORD'])
            for host in 
            ['http://{}:{}@localhost:9200/',
            'http://{}:{}@ip-10-0-0-8:9200/',
            'http://{}:{}@ip-10-0-0-7:9200/',
            'http://{}:{}@ip-10-0-0-5:9200/']
        ]
        self.es = Elasticsearch(hosts, timeout=900)
        
    def random_topics(self):
        seed = randint(-100000, 100000)
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
        results = self.es.search(index="gdelt", body=query)
        return results['hits']['hits'][0]['_source']['topics']
    
    def get_counts(self, topics):
        counts = []
        for t in topics:
            query = {
                "query": {
                    "match": {"topics": t}
                }
            }
            count = self.es.count(index="gdelt", body=query)['count']
            counts.append((t, count))
        return counts
    
    def filter_by_count(self, counts, threshold=3*10**6):
        return [c[0] for c in counts if c[1] < threshold]
    
    def topic_query(self, topics):
        query = {
            'size':10,
            "query": {
                "match": {"topics": ' '.join(topics)}
            }
        }
        results = self.es.search(index="gdelt", body=query)
        records = [record['_source'] for record in results['hits']['hits']]
        return {
            'results': records, 
            'took': results['took'],
            'hits': results['hits']['total']
        }
    
    def custom_score(self, topics):
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
        results = self.es.search(index="gdelt", body=query)
        records = [record['_source'] for record in results['hits']['hits']]
        return {
            'results': records, 
            'took': results['took'],
            'hits': results['hits']['total']
        }
    
        
        
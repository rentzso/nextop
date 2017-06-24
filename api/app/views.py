from flask import request
from flask import json
from flask import render_template
from app import app
from elasticsearch import Elasticsearch
import os
from random import randint

hosts = [
    'http://{}:{}@{}:9200/'.format(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS'], host)
    for host
    in os.environ['ELASTIC_HOSTS'].split(',')
    ]

es = Elasticsearch(hosts, timeout=90)

@app.route('/nextop', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/topics', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    topics = data['topics']
    simple = data.get('simple', True)
    if simple:
        return json.dumps(query_simple(topics))
    else:
        return json.dumps(query_custom(topics))

@app.route('/random')
def get_random():
    seed = randint(-10**6, 10**6)
    query = {
        "size": 1,
        "query": {
            "function_score": {
                "query": {
                    "range": {
                        "num_topics": {
                            "lte": 7,
                            "gte": 4
                        }
                    }
                },
                "random_score": {
                    "seed": seed
                }
            }
        }
    }
    return json.dumps(_exec_query(query)[0])

@app.route('/stats')
def get_stats():
    return json.dumps({
        'false': _exec_query(get_query_stats('false'), 'users'),
        'true': _exec_query(get_query_stats('true'), 'users')
    })

def get_query_stats(score_type):
    return {
        "size" : 10,
        "sort" : [
            { "id" : {"order" : "desc"}}
        ],
        "query" : {
            "match" : {"score_type": score_type}
        }
    }

def query_custom(topics):
    should_clause = [
        {'constant_score': {
            'filter' : {
                'match': { 'topics' :  topic} }}}
        for topic in topics
    ]
    query = {
        'size': 10,
        'query': {
            'function_score': {
                'query': {
                    'bool': {'should': should_clause }
                },
                'script_score' : {
                    'script' : {
                        'inline': '- Math.abs(_score/doc[\'num_topics\'].value - 0.75)'
                    }
                }
            }
        }
    }
    return {'recommendations': _exec_query(query)}

def query_simple(topics):
    should_clause = [
        {'match': { 'topics' :  topic} }
        for topic in topics
    ]
    query = {
        'size': 10,
        'query': {
            'bool': {'should': should_clause}
        }
    }
    return {'recommendations': _exec_query(query)}

def _exec_query(query, index='documents'):
    results = es.search(index=index, body=query)
    app.logger.info('a simple request took {} milliseconds'.format(results['took']))
    parsed_results = []
    for result in results['hits']['hits']:
        parsed_result = result['_source']
        parsed_result['score'] = result['_score']
        parsed_results.append(parsed_result)
    return parsed_results

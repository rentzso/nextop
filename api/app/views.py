from flask import request
from flask import json
from flask import render_template
from app import app
from elasticsearch import Elasticsearch
import os
from random import randint

hosts = [
    'http://{}:{}@{}:9200/'.format(
        os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS'], host)
    for host
    in os.environ['ELASTIC_HOSTS'].split(',')
    ]

es = Elasticsearch(hosts, timeout=90)


@app.route('/nextop', methods=['GET'])
def index():
    return render_template(
        'index.html', window=int(os.environ.get('UI_WINDOW', 120))*1000,
        slide=int(os.environ.get('UI_SLIDE', 5))*1000
        )


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
        'size': 1,
        'query': {
            'function_score': {
                'query': {
                    'range': {
                        'num_topics': {
                            'gte': 4,
                            'lte': 7
                        }
                    }
                },
                'random_score': {
                    'seed': seed
                }
            }
        }
    }
    recommendations, took = _exec_query(query)
    return json.dumps({
        'recommendations': recommendations,
        'took': took
    })


@app.route('/stats')
def get_stats():
    timestamp = request.args.get('from')
    statistics, took = _exec_query(get_query_stats(timestamp), 'users')
    return json.dumps({
        'statistics': statistics,
        'took': took
    })


def get_query_stats(timestamp):
    return {
        'size': 10000,
        'query': {
            'range': {
                'timestamp': {
                    'gte': timestamp
                }
            }
        }
    }


def query_custom(topics):
    should_clause = [
        {'constant_score': {
            'filter': {
                'match': {'topics':  topic}}}}
        for topic in topics
    ]
    script = '- Math.abs(_score/doc[\'num_topics\'].value - 0.75)'
    query = {
        'size': 10,
        'query': {
            'function_score': {
                'query': {
                    'bool': {
                        'should': should_clause,
                        'filter': {
                            'range': {
                                'num_topics': {
                                    'gte': 1,
                                    'lte': len(topics)
                                }
                            }
                        }
                    }
                },
                'script_score': {
                    'script': {
                        'inline': script
                    }
                }
            }
        }
    }
    recommendations, took = _exec_query(query)
    return {
        'recommendations': recommendations,
        'took': took
    }


def query_simple(topics):
    should_clause = [
        {'match': {'topics':  topic}}
        for topic in topics
    ]
    query = {
        'size': 10,
        'query': {
            'bool': {'should': should_clause}
        }
    }
    recommendations, took = _exec_query(query)
    return {
        'recommendations': recommendations,
        'took': took
    }


def _exec_query(query, index='documents'):
    results = es.search(index=index, body=query)
    app.logger.info(
        'a simple request took {} milliseconds'.format(results['took']))
    parsed_results = []
    for result in results['hits']['hits']:
        parsed_result = result['_source']
        parsed_result['score'] = result['_score']
        parsed_results.append(parsed_result)
    return parsed_results, results['took']

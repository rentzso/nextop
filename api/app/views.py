"""
This module includes all the API endpoints used in the flask API.

/nextop - the UI entrypoint
/topics - receives a list of topics and returning recommendations
/random - returns a random document
/stats  - returns the latest user statistics
"""

from flask import request
from flask import json
from flask import render_template
from app import app
from elasticsearch import Elasticsearch
import os
from random import randint

# Builds the list of Elasticsearch hosts
hosts = [
    'http://{}:{}@{}:9200/'.format(
        os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS'], host)
    for host
    in os.environ['ELASTIC_HOSTS'].split(',')
    ]

# Creates the Elasticsearch client
es = Elasticsearch(hosts, timeout=90)


@app.route('/nextop', methods=['GET'])
def index():
    """
    Renders the index.html template.

    Takes as parameter the time window to show for the scatterplot.
    """
    return render_template(
        'index.html', window=int(os.environ.get('UI_WINDOW', 120))*1000
        )


@app.route('/topics', methods=['POST'])
def get_recommendations():
    """
    Handles a request for recommendations.

    The json payload should contain two parameters:
    topics - a list of favorite user topics
    simple - defines the type of recommendation used (optional, default: True)
    """
    data = request.get_json()
    topics = data['topics']
    simple = data.get('simple', True)
    if simple:
        return json.dumps(query_simple(topics))
    else:
        return json.dumps(query_custom(topics))


@app.route('/random')
def get_random():
    """
    Returns a random news article from the database.

    The only constraint is the number of topics (between 4 and 7).
    This is used to initialize a simulated user.
    """
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
    """
    Returns the latest user statistics.

    params:
    from - earliest timestamp for which we return statistics
    """
    timestamp = request.args.get('from')
    statistics, took = _exec_query(get_query_stats(timestamp), 'users')
    return json.dumps({
        'statistics': statistics,
        'took': took
    })


def get_query_stats(timestamp):
    """
    Builds the query to retrieve user statistics from Elasticsearch.
    """
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
    """
    Requests for recommendations with the custom scoring system.

    We retrieve all the documents with at least one topic in common with the input (user) topics.
    Each matching topic contributes to the _score of a document for a constant score of 1.
    This _score is then normalized by dividing it by the number of document topics.
    The actual relevance depends then from the distance of this normalized score from 0.75.
    In this way we ensure that approximately 3/4 of document topics are matching with the user topics.
    """
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
    """
    Requests for recommendations with the simple scoring system.

    We retrieve all the documents with at least one topic in common with the input (user) topics.
    Each matching topic score (using the default tf-idf like scoring) is summed up to give the score used
    in the document ranking.
    """
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
    """
    Returns a list of results and the time the query took to execute in Elasticsearch.

    Input arguments:
    query - the query executed
    index - the Elasticsearch index on which the query needs to be executed.
    """
    results = es.search(index=index, body=query)
    app.logger.info(
        'a simple request took {} milliseconds'.format(results['took']))
    parsed_results = []
    for result in results['hits']['hits']:
        parsed_result = result['_source']
        parsed_result['score'] = result['_score']
        parsed_results.append(parsed_result)
    return parsed_results, results['took']

# nexTop

My project for the Insight Data Engineering Summer 2017 session is a content discovery system of news articles based on topics.<br>
The general idea is to recommend to the users contents that are relevant but also new and fresh. The main component used to do this is Elasticsearch and its flexible scoring system. Elasticsearch allowed to implement and compare two recommendation systems, one using a more traditional tf-idf relevance score and another, the nexTop scoring system, designed to deliver recommendations with a mix of topics, some relevant, some new to the users ([details here](#supported-recommendations)).

[Slides of the presentation](https://docs.google.com/presentation/d/19dMRsMbs9zlJMDJpl5r7eY-QOlvzOLiLVmAlL-bc98w).

# The architecture

The main components are:
- The ingestion pipeline collecting data from the GDELT Dataset into Elasticsearch
- The Flask API matching user topics with document topics in Elasticsearch and returning recommendations
- The user simulation component, generating user clicks based on the two recommendation systems available and collecting statistics

![nexTop architecture](/../images/img/Architecture.png?raw=true "nexTop architecture")

## The ingestion pipeline

To load data into Elasticsearch, I created one Kafka Producer reading and parsing data from the [GDELT S3 Dataset](https://aws.amazon.com/public-datasets/gdelt/) into an [Avro schema](https://github.com/rentzso/producerS3/blob/master/src/main/resources/avroSchemas/parsed-gdelt-avro-schema.json).<br>
Each parsed record (news url, date, related topics) was published to a Kafka topic.<br>
The messages were read by a Spark Streaming consumer and stored into Elasticsearch via the native client library elasticsearch-hadoop.

Ingestion pipeline repositories:
- [Kafka producer connected to S3](https://github.com/rentzso/producerS3)
- [Spark Streaming consumer](https://github.com/rentzso/newsStreaming)

## The Flask API

The Flask API ([code](https://github.com/rentzso/nextop/blob/master/api/app/views.py)) provides an interface to Elasticsearch:
- GET `/random` returns a random document
- POST `/topics` takes a list of user topics and the desired recommendation type and returns a set of news recommendations
- GET `/stats` returns the last data points of the user statistics
- GET `/` returns a dashboard showing how many new topics the two groups of users are exposed to

### Supported recommendations

For the `topics` endpoint there are two recommendation (and score) types implemented at the moment:
- **simple** - the default Elasticsearch score (Okapi BM25, a tf-idf-like similarity score)
- **custom** - a scripted custom score

Both recommendations receive a list of user topics and find the best scores among the list of all documents which have at least one matching topic.<br>
The **simple** recommendation type ([code](https://github.com/rentzso/nextop/blob/master/api/app/views.py#L183)) computes its score summing up all the Elasticsearch scores from the matching user topics. In this setup a less frequent topic will contribute more than a common topic to the final score and the top scorers will be the documents matching more user topics.<br>
In the **custom** recommendation ([code](https://github.com/rentzso/nextop/blob/master/api/app/views.py#L142)), for a news article its score is the ratio of matched user topics over the number of topics related to the document. So each matching topic contributes equally to the final score, and all the scores are in the range 0 to 1. The recommended news are not the top scorers but rather the documents with the scores closest to a configurable target score (0.75 at the moment). This means that a recommendation will require a minimum number of matching topics but also a minimum number of non matching, fresh topics.

## The user simulation component

This component generates user behavior (sequences of user clicks) by using the Flask API recommendations multiple times.
It then collects the simulated user statistics and, using a Kafka Producer, publishes them as Avro messages ([schema](https://github.com/rentzso/simulatedUser/blob/master/src/main/resources/avroSchemas/user-stats-avro-schema.json)) to a Kafka topic.
A Spark Streaming consumer reads from the Kafka topic and stores the statistics on Elasticsearch.

Simulation component repositories:
- [User simulator and Kafka Producer](https://github.com/rentzso/simulatedUser)
- [Spark Streaming consumer](https://github.com/rentzso/userStatsStreaming)

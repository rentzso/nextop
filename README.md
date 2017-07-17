# nexTop - Insight Summer 2017

NexTop is my project for Insight Summer 2017. It is a content discovery system of news articles based on topics.<br>
The general idea is to recommend to the users contents that are relevant but also new to them.

## How it works
- Uses the GDELT dataset from the Global Knowledge Graph
- Extracts the topics from each record in the dataset
- Loads the GDELT news and the related topics in the Elasticsearch database
- Keeps a list of the news each user visited and of the most frequent topics
- Based on these topics computes the most relevant news articles using a customizable scoring system
- Simulates user clicks based on these recommendations
- Collects statistics from this simulation

There are two recommendation (and score) types available at the moment:
- **simple** - the default Elasticsearch score (Okapi BM25, a tf-idf-like similarity score)
- **custom** - a scripted score computing the ratio of matched topics over total number of topics

# The architecture

![nexTop architecture](/../images/img/Architecture.png?raw=true "nexTop architecture")

The main components are:
- The ingestion pipeline collecting data from GDELT into Elasticsearch
- The Flask API matching user topics with document topics and returning recommendations
- The simulation pipeline, generating user clicks based on the two recommendation systems available and collecting statistics

## The ingestion pipeline

To load data into Elasticsearch, I created one Kafka Producer reading and parsing data from the [GDELT S3 Dataset](https://aws.amazon.com/public-datasets/gdelt/) into an [Avro schema](https://github.com/rentzso/producerS3/blob/master/src/main/resources/avroSchemas/parsed-gdelt-avro-schema.json).<br>
Each parsed record (news url, date, related topics) was published to a Kafka topic.<br>
The messages were read by a Spark Streaming consumer and stored into Elasticsearch via the native client library elasticsearch-hadoop.

Ingestion pipeline repositories:
- [Kafka producer connected to S3](https://github.com/rentzso/producerS3)
- [Spark Streaming consumer](https://github.com/rentzso/newsStreaming)

## The Flask API

In the folder `api` of this repo there is a flask API providing an interface to Elasticsearch:
- GET `/random` returns a random document
- POST `/topics` takes a list of topics and the recommendation type and returns a news recommendation
- GET `/stats` returns the last data points of the user statistics
- GET `/` returns a dashboard showing how many new topics the two groups of users are exposed to

## The simulation pipeline

This pipeline generates user clicks with a Kafka Producer to simulate user behavior and to store the click information in a Kafka topic.<br>
A Spark Streaming process reads from the Kafka topic and stores these statistics on Elasticsearch.

Simulation pipeline repositories:
- [Kafka Producer](https://github.com/rentzso/simulatedUser)
- [The Spark Streaming consumer](https://github.com/rentzso/userStatsStreaming)

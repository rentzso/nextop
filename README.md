# NexTop
Content discovery engine project - Insight Summer 2017

## How it works
- Uses the GDELT dataset from the Global Knowledge Graph
- Extracts the topics from each record
- Loads the GDELT news and the related topics in the Elasticsearch database
- Keeps a list of the news each user visited and of the most frequent topics
- Based on these topics computes the most relevant news articles using a customizable scoring system
- Simulates user clicks based on these recommendations
- Collects statistics from this simulation

There are two recommendations (and score types) available at the moment:
- **simple** - the default Elasticsearch score
- **custom** - with a scripted score computing the ratio of matched topics over total number of topics


# The architecture

![nexTop architecture](/../images/img/Architecture.png?raw=true "nexTop architecture")

The main component are:
- The ingestion pipeline collecting data from GDELT into Elasticsearch
- The Flask API matching user topics with recommendations
- The simulation pipeline, generating user clicks based on the two recommendation systems available and collecting statistics

## The ingestion pipeline

To load data into Elasticsearch, I created one Kafka Producer to load data from S3 into a Kafka topic.<br>
A Spark Streaming job was pulling the messages from the topic and transfering the data into Elasticsearch via the native client library elasticsearch-hadoop.

Ingestion pipeline repositories:
- https://github.com/rentzso/producerS3 - the Kafka producer connected to S3
- https://github.com/rentzso/newsStreaming - the Spark Streaming consumer

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
- https://github.com/rentzso/simulatedUser - The Kafka Producer
- https://github.com/rentzso/userStatsStreaming - The Spark Streaming consumer


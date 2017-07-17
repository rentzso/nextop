# nexTop

NexTop is my project for the Insight Summer 2017 session, a content discovery system of news articles based on topics.<br>
The general idea is to recommend to the users contents that are relevant but also new and fresh.<br>
The system has three main functional components (see also the [architecture](#the-architecture) section):
- Collecting and storing news urls for the recommendations
- Generating the recommendations using multiple scoring systems
- Comparing the recommendation systems

In more detail these are the high level steps performed by nexTop:
- Reads news urls from [the GDELT dataset](https://aws.amazon.com/public-datasets/gdelt/)
- Extracts the topics from each record in the dataset
- Loads the GDELT news and the related topics in the Elasticsearch database
- Keeps a list of the news each user visited and of the topics she was exposed to
- Based on these topics computes the most relevant news articles using a customizable scoring system
- Simulates user clicks based on these recommendations
- Collects statistics from this simulation

These are [the slides of my presentation](https://docs.google.com/presentation/d/19dMRsMbs9zlJMDJpl5r7eY-QOlvzOLiLVmAlL-bc98w).

# The architecture

![nexTop architecture](/../images/img/Architecture.png?raw=true "nexTop architecture")

The main components are:
- The ingestion pipeline collecting data from the GDELT Dataset into Elasticsearch
- The Flask API matching user topics with document topics in Elasticsearch and returning recommendations
- The simulation pipeline, generating user clicks based on the two recommendation systems available and collecting statistics

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

For the `topics` endpoint there are two recommendation (and score) types used by the system at the moment:
- **simple** - the default Elasticsearch score (Okapi BM25, a tf-idf-like similarity score)
- **custom** - a scripted custom score

Both recommendations receive a list of user topics and finds the best scores among the list of all documents which have at least one matching topic.<br>
The **simple** recommendation type ([code](https://github.com/rentzso/nextop/blob/master/api/app/views.py#L183)) computes its score summing up all the Elasticsearch scores from the matching user topic. In this setup a less frequent topic will contribute more than a common topic to the final score and the top scorers will be the documents matching more user topics.<br>
In the **custom** recommendation ([code](https://github.com/rentzso/nextop/blob/master/api/app/views.py#L142)), for a news article the score is the ratio of matched user topics over the number of topics related to the document. So each matching topic contributes for the same amount to the final score, and all the scores are in the range `[0, 1]`. However the recommended news are not the top scorers but rather the documents with the scores closest to a configurable target score (0.75 at the moment). This means that a recommendation will require a minimum number of matching topics but also a minimum number of non matching, fresh topics.

## The simulation pipeline

This pipeline generates user clicks with a Kafka Producer to simulate user behavior and to store the click information in a Kafka topic.<br>
A Spark Streaming process reads from the Kafka topic and stores these statistics on Elasticsearch.

Simulation pipeline repositories:
- [Kafka Producer that simulates users](https://github.com/rentzso/simulatedUser)
- [Spark Streaming consumer](https://github.com/rentzso/userStatsStreaming)

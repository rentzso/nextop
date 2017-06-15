# NexTop
Content discovery engine project - Insight Summer 2017

## How it works
Uses the GDELT dataset from the Global Knowledge Graph
Extracts the topics from each record Loads the GDELT news and the related topics in the Elasticsearch database
Keeps a list of the news each user visited and of the most frequent topics Based on this topics computes the most relevant news articles using a customizable scoring system

# How to run it
There is a script to load the data into Elasticsearch: `src/data_loadingi.py`
Then, the main `run.sh` program can simulate a user navigating, first, on a random article, then following NexTop recommendations.

# Additional repositories
For fast data ingestion I developed this two small Scala libraries:
- https://github.com/rentzso/producerS3 - a Kafka producer connected to S3
- https://github.com/rentzso/newsStreaming - a Spark Streamin consumer using Elastic native client library
# NexTop
Content discovery engine project - Insight Summer 2017

## How it works
Uses the GDELT dataset from the Global Knowledge Graph<br>
Extracts the topics from each record Loads the GDELT news and the related topics in the Elasticsearch database<br>
Keeps a list of the news each user visited and of the most frequent topics Based on this topics computes the most relevant news articles using a customizable scoring system<br>

# How to run it
It depends on the elasticsearch python client.<br>
To load the data into Elasticsearch, there is a script `src/data_loading.py`<br>
Then, the `run.sh` program can simulate a user navigating, first, on a random article, then following NexTop recommendations.

# Additional repositories
For fast data ingestion I developed this two small Scala libraries:
- https://github.com/rentzso/producerS3 - a Kafka producer connected to S3
- https://github.com/rentzso/newsStreaming - a Spark Streamin consumer using Elastic native client library
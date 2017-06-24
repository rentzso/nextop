# NexTop
Content discovery engine project - Insight Summer 2017

## How it works
Uses the GDELT dataset from the Global Knowledge Graph<br>
Extracts the topics from each record Loads the GDELT news and the related topics in the Elasticsearch database<br>
Keeps a list of the news each user visited and of the most frequent topics <br>
Based on these topics computes the most relevant news articles using a customizable scoring system<br>
There are two score types available at the moment:
- **simple** - the default Elasticsearch score
- **custom** - with a scripted score computing the ratio of matched topics over total number of topics

# How to run it
It depends on the elasticsearch python client.<br>
To load the data into Elasticsearch, there is a script `src/data_loading.py`<br>
Then, the `run.sh` program can simulate a user navigating, first, on a random article, then following NexTop recommendations.

# The Flask API

In the folder `api` there is a flask API providing an interface to Elasticsearch:
- GET `/random` returns a random document
- POST `/topics` takes a list of topics with the score type and returns a news recommendation
- GET `/stats` returns the last data points of the user statistics


# Additional repositories
For fast data ingestion I developed this two Scala libraries:
- https://github.com/rentzso/producerS3 - a Kafka producer connected to S3
- https://github.com/rentzso/newsStreaming - a Spark Streamin consumer using Elastic native client library
Other two libraries were created to collect user statistics:
- https://github.com/rentzso/simulatedUser - to simulate user behavior and send individual statistics to Kafka
- https://github.com/rentzso/userStatsStreaming - to compute the average number of topics a user ws exposed
To enable scripting on elasticsearch, it is necessary to follow these steps:
1) enable groovy in elasticsearch.xml with this line:
```
script.engine.groovy.inline: on
```
2) create the index with a mapping on topics with index_options freqs
```
curl --user $ELASTIC_USER:$ELASTIC_PASSWORD -XPUT 'localhost:9200/documents?pretty' -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "news": {
      "properties": {
        "topics": {
          "type": "text",
          "index_options": "freqs"
        }
      }
    }
  }
}
'
```
3) enable "fielddata" on the field "topics"
```
curl --user $ELASTIC_USER:$ELASTIC_PASSWORD -XPUT 'localhost:9200/documents/_mapping/news?pretty' -H 'Content-Type: application/json' -d'
{
  "properties": {
    "topics": {
      "type":     "text",
      "fielddata": true
    }
  }
}
'
```

Also it's needed to disable the index refresh before bulk uploads.


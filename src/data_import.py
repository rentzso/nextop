import csv
import os
import tempfile
from datetime import datetime
from elasticsearch import Elasticsearch
from boto.s3.connection import S3Connection

es_client = Elasticsearch()

## from http://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook-V2.1.pdf
FIELD_NAMES = [
    'GKGRECORDID',
    'V2.1DATE',
    'V2SOURCECOLLECTIONIDENTIFIER',
    'V2SOURCECOMMONNAME',
    'V2DOCUMENTIDENTIFIER',
    'V1COUNTS',
    'V2.1COUNTS',
    'V1THEMES',
    'V2ENHANCEDTHEMES',
    'V1LOCATIONS',
    'V2ENHANCEDLOCATIONS',
    'V1PERSONS',
    'V2ENHANCEDPERSONS',
    'V1ORGANIZATIONS',
    'V2ENHANCEDORGANIZATIONS',
    'V1.5TONE',
    'V2.1ENHANCEDDATES',
    'V2GCAM',
    'V2.1SHARINGIMAGE',
    'V2.1RELATEDIMAGES',
    'V2.1SOCIALIMAGEEMBEDS',
    'V2.1SOCIALVIDEOEMBEDS',
    'V2.1QUOTATIONS',
    'V2.1ALLNAMES',
    'V2.1AMOUNTS',
    'V2.1TRANSLATIONINFO',
    'V2EXTRASXML'
]

def get_key_list(bucket_name, folder):
    conn = S3Connection(os.environ['AWS_ACCESS_KEY_ID'],os.environ['AWS_SECRET_ACCESS_KEY'])
    bucket = conn.get_bucket(bucket_name)
    for key in bucket.list(prefix=folder, marker=folder):
        yield key

def read_csv(key):
    tmpfile = '/tmp/s3.csv'
    key.get_contents_to_filename(tmpfile)
    rows = csv.reader(tmpfile, delimiter='\t')
    for row in rows:
        yield dict(zip(FIELD_NAMES, row))

def parse_record(record):
    topics = record['V1THEMES'].split(';').extend(record['V2ENHANCEDTHEMES'].split(';'))
    url = record['V2DOCUMENTIDENTIFIER'] if record['V2SOURCECOLLECTIONIDENTIFIER'] else None
    return {
        'id': record['GKGRECORDID'],
        'date': record['V2.1DATE'],
        'topics': topics,
        'url': url
    }

def send_to_elastic(entry):
    if entry['url'] is not None:
        uid = entry.pop('id')
        es.index(index='documents', doc_type='news', body=entry, id = uid)

def main():
    bucket_name = "gdelt-open-data"
    folder = "v2/gkg"
    keys = get_key_list(bucket_name, folder)
    for i, key in enumerate(keys):
        if i == 2:
            break
        records = read_csv(key)
        for record in records:
            entry = parse_record(record)
            send_to_elastic(entry)

if __name__ == '__main__':
    main()








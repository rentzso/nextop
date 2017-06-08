import csv
import os
import tempfile
from datetime import datetime
from elasticsearch import Elasticsearch
from boto.s3.connection import S3Connection

host = 'http://{}:{}@localhost:9200/'.format(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASSWORD'])
es_client = Elasticsearch(
    [host]
)

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

def read_csv(tmpfile):
    with open(tmpfile, 'rU') as f:
        rows = csv.DictReader(f, fieldnames=FIELD_NAMES, delimiter='\t')
        # iterate within the context manager to avoid "I/O operation on closed file" error
        for row in rows:
            yield row


def parse_record(record):
    topics = record['V1THEMES'].split(';') if record['V1THEMES'] else None
    if topics is not None and len(topics) and topics[-1] == '':
        topics = topics[:-1]
    date = datetime.strptime(record['V2.1DATE'], '%Y%m%d%H%M%S')
    return {
        'id': record['GKGRECORDID'],
        'date': date,
        'topics': topics,
        'url': record['V2DOCUMENTIDENTIFIER']
    }

def send_to_elastic(entry):
    if entry['url'] is not None:
        uid = entry.pop('id')
        es_client.index(index='documents', doc_type='news', body=entry, id = uid)

def main():
    bucket_name = 'gdelt-open-data'
    folder = 'v2/gkg'
    tmpfile = '/tmp/s3.csv'
    keys = get_key_list(bucket_name, folder)
    for i, key in enumerate(keys):
        if i == 1:
            break
        key.get_contents_to_filename(tmpfile)
        records = read_csv(tmpfile)
        for record in records:
            if record['V2SOURCECOLLECTIONIDENTIFIER'] == '1':
                entry = parse_record(record)
                print entry
                send_to_elastic(entry)

if __name__ == '__main__':
    main()








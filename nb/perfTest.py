from utilEs import Queries
import sys

def main(n=100):
    q = Queries()
    for i in xrange(n):
        original_topics = q.random_topics()
        try:
            counts = q.get_counts(original_topics)
            topics = q.filter_by_count(counts)
            res = q.topic_query(topics)
            print 'filtered', res['hits'], res['took'], len(topics)
            urls = set([r['url'] for r in res['results']])        
            orig_res = q.topic_query(original_topics)
            print 'original', orig_res['hits'], orig_res['took'], len(original_topics)
            orig_urls = set([r['url'] for r in orig_res['results']])
            if urls.difference(orig_urls):
                print urls.difference(orig_urls)
                print orig_urls.difference(urls)
        except:
            pass
            
        
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        main()
    else:
        main(int(sys.argv))
    
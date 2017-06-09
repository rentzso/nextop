import sys
import elasticsearch
import db

def main():
    start_document = db.getRandomNews()
    print start_document['url']
    print 'Topics: ', start_document['topics'], '\n'
    topics = set(start_document['topics'])
    while True:
        recommendations = db.getRecommendations(topics)
        for i, r in enumerate(recommendations):
            print i + 1, ' -> ', r['url']
        print
        selected = raw_input('select a news article(0 to exit): ')
        print
        try:
            selected = int(selected) - 1
        except:
            selected = -1
        if selected == -1:
            break
        new_topics = recommendations[selected]['topics']
        print recommendations[selected]['url']
        print 'Topics: ', new_topics, '\n'
        topics = topics.union(new_topics)

if __name__ == '__main__':
    main()

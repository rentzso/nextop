import sys
import elasticsearch
import db



def main():
    start_document = db.getRandomNews()
    print start_document['url'] + '\n'
    topics = set(start_document['topics'])
    while True:
        recommendations = db.getRecommendations(topics)
        for i, r in enumerate(recommendations):
            print i + 1, r['url']
        selected = raw_input('select a news article(0 to exit): ')
        try:
            selected = int(selected) - 1
        except:
            selected = -1
        if selected == -1:
            break
        topics = topics.union(recommendations[selected])

if __name__ == '__main__':
    main()

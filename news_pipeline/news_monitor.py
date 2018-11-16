"""
responsible for finding new news by using News API
By calling articles api (https://newsapi.org/v1/articles)
periodically, we will get news from the specific source (https://newsapi.org/sources)
we provided.
Articles api (https://newsapi.org/docs/v1#apiArticles) handle a GET request.
Use Redis to store the hash of the news we recently fetched so that we can avoid to
process identical news more than once.
News Schema
primary key: digest: MD5 hash of news title.
title, description, text, url, author (can be null), source
publishedAt: match the return object from News API
urlToImage, class (for recommendation)
"""
import datetime
import hashlib
import logging
import redis
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import news_api_client
from cloudAMQP_client import CloudAMQPClient

logger_format = '%(asctime)s - %(message)s'
logging.basicConfig(format=logger_format)
logger = logging.getLogger('news_monitor')
logger.setLevel(logging.DEBUG)

#usually sleep 5 minutes
SLEEP_TIME_IN_SECONDS = 10
#check duplicate within 3 days
NEWS_TIME_OUT_IN_SECONDS = 3600 * 24 * 3

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

SCRAPE_NEWS_TASK_QUEUE_URL = "xxx"
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap-news-scarpe-news-task-queue"

NEWS_SOURCES = [
    'bbc-news',
    'bbc-sport',
    'bloomberg',
    'cnn',
    'entertainment-weekly',
    'espn',
    'ign',
    'techcrunch',
    'the-new-york-times',
    'the-wall-street-journal',
    'the-washington-post'
]

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
cloudAMQP_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)


def run():
    while True:
        news_list = news_api_client.getNewsFromSources(NEWS_SOURCES)
        #record new coming xinwen
        num_of_new_news = 0
        # find duplidate xinwen, hash title
        for news in news_list:
            news_digest = hashlib.md5(news['title'].encode('utf-8')).hexdigest()
            
            if redis_client.get(news_digest) is None:
                num_of_new_news += 1
                news['digest'] = news_digest
                
                if news['publishedAt'] is None:
                    news['publishedAt'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                
                redis_client.set(news_digest, 'True')
                redis_client.expire(news_digest, NEWS_TIME_OUT_IN_SECONDS)
                
                cloudAMQP_client.sendMessage(news)
        
        logger.info('Fetched %d news.', num_of_new_news)
        cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)


if __name__ == '__main__':
    run()

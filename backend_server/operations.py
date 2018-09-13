"""Backend service"""
import json
import os
import sys
import redis
import pickle

from bson.json_util import dumps
from datetime import datetime

# import utils dir to rightnow filepath, intend to import mongodb
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from cloudAMQP_client import CloudAMQPClient
import mongodb_client  # pylint: disable=import-error, wrong-import-position
import news_recommendation_service_client

REDIS_HOST = "localhost"
REDIS_PORT = 6379
USER_NEWS_TIME_OUT_IN_SECONDS = 3600 #redis sleep

NEWS_TABLE_NAME = "news"
NEWS_LIMIT = 100 # each time 100ge news
NEWS_LIST_BATCH_SIZE = 10 #each page 10 news

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)

LOG_CLICKS_TASK_QUEUE_URL = "amqp://mpxyrqme:164-72skmB8Kk4QFkPHTb5ZDmzQX51lp@otter.rmq.cloudamqp.com/mpxyrqme"
LOG_CLICKS_TASK_QUEUE_NAME = "tap-news-log-clicks-task-queue"

cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)


def add(num1, num2):
    return num1 + num2


def get_one_news():
    res = mongodb_client.get_db()['news'].find_one()
    # dumps(res): convert bson to string
    # then convert string to json
    return json.loads(dumps(res))


def get_news_summaries_for_user(user_id, page_num):
    page_num = int(page_num)
    if page_num <= 0:
        return []
        
    begin_index = (page_num - 1) * NEWS_LIST_BATCH_SIZE
    end_index = page_num * NEWS_LIST_BATCH_SIZE

    # The final list of news to be returned.
    sliced_news = []
    db = mongodb_client.get_db()

    if redis_client.get(user_id) is not None:
        #redis only store news digest(id), and based on this id look up from mongodb
        #pickle:store obj/instance to file as string (xuliehua)
        news_digests = pickle.loads(redis_client.get(user_id))
        
        sliced_news_digests = news_digests[begin_index:end_index]
        sliced_news = list(db[NEWS_TABLE_NAME].find({'digest':{'$in':sliced_news_digests}}))

    else:
        total_news = list(db[NEWS_TABLE_NAME].find().sort([('publishedAt', -1)]).limit(NEWS_LIMIT))
        total_news_digests = [x['digest'] for x in total_news]
        
        redis_client.set(user_id, pickle.dumps(total_news_digests))
        redis_client.expire(user_id, USER_NEWS_TIME_OUT_IN_SECONDS)
        
        sliced_news = total_news[begin_index:end_index]

    # Get preference list for the user.
    # TODO: use preference to customize returned news list.
    preference = news_recommendation_service_client.getPreferenceForUser(user_id)
    topPreference = None
    
    if preference is not None and len(preference) > 0:
        topPreference = preference[0]
    
    for news in sliced_news:
        # Remove text field to save bandwidth.
        del news['text']
        if news['publishedAt'].date() == datetime.today().date():
            news['time'] = 'today'
        if news['class'] == topPreference:
            news['reason'] = 'Recommend'

    return json.loads(dumps(sliced_news))


def log_news_click_for_user(user_id, news_id):
    message = {'userId': user_id, 'newsId': news_id, 'timestamp': str(datetime.utcnow())}
    
    # Send log task to recommendation service.
    cloudAMQP_client.sendMessage(message)

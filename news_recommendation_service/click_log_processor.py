'''
Time decay model:
If selected:
p = (1-α)p + α
If not:
p = (1-α)p
Where p is the selection probability, and α is the degree of weight decrease.
The result of this is that the nth most recent selection will have a weight of
(1-α)^n. Using a coefficient value of 0.05 as an example, the 10th most recent
selection would only have half the weight of the most recent. Increasing epsilon
would bias towards more recent results more.
'''

import logging
import news_classes
import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
from cloudAMQP_client import CloudAMQPClient

# 8 class of topic
NUM_OF_CLASSES = 8
# each topic is 1/8
INITIAL_P = 1.0 / NUM_OF_CLASSES
# If selected: p = (1 - α) * p + α, If not selected: p = (1 - α) * p
ALPHA = 0.1

SLEEP_TIME_IN_SECONDS = 1  # Optinal

LOG_CLICKS_TASK_QUEUE_URL = "amqp://mpxyrqme:164-72skmB8Kk4QFkPHTb5ZDmzQX51lp@otter.rmq.cloudamqp.com/mpxyrqme"
LOG_CLICKS_TASK_QUEUE_NAME = "tap-news-log-clicks-task-queue"

# define mongodb table name
PREFERENCE_MODEL_TABLE_NAME = "user_preference_model"
# "news" table from mongodb
NEWS_TABLE_NAME = "news"

LOGGER_FORMAT = "%(asctime)s - %(message)s"
logging.basicConfig(format=LOGGER_FORMAT)
LOGGER = logging.getLogger('click_log_processor')
LOGGER.setLevel(logging.DEBUG)

cloudAMQP_client = CloudAMQPClient(LOG_CLICKS_TASK_QUEUE_URL, LOG_CLICKS_TASK_QUEUE_NAME)

def handle_message(msg):
    if msg is None or not isinstance(msg, dict):
        return
    #if any of these three missing, return
    if ('userId' not in msg
        or 'newsId' not in msg
        or 'timestamp' not in msg):
        return
    
    userId = msg['userId']
    newsId = msg['newsId']
    
    # Update user's preference model
    db = mongodb_client.get_db()
    # find preference model based on useID
    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId':userId})
    
    # If model not exists, create a new one.
    if model is None:
        LOGGER.info('Creating preference model for new user: %s', userId)
        """
        model{
            'userId': userId,
            'preference':{
                'sports':0.2,
                'game': 0.3,
                'world':0.5
            }
        }
        """
        new_model = {'userId':userId}
        preference = {}
        for i in news_classes.classes:
            # preference['word'] = 0.125
            # preferendce['us'] = 0.125
            preference[i] = INITIAL_P
        # add preference string to model
        new_model['preference'] = preference
        model = new_model
    
    LOGGER.info('Updating preference model for user: %s', userId)
    
    # Update model using time decay model.
    # add/ modify all need update, wo replace_one
    news = db[NEWS_TABLE_NAME].find_one({'digest':newsId})
    if (news is None
        or 'class' not in news
        or news['class'] not in news_classes.classes):
        return
    
    click_class = news['class']
    
    # Update the clicked one.
    #old_p: original class %
    old_p = model['preference'][click_class]
    model['preference'][click_class] = float((1 - ALPHA) * old_p + ALPHA)
    
    # Update not clicked classes.
    for i, prob in model['preference'].items():
        if not i == click_class:
            old_p = model['preference'][i]
            #update %
            model['preference'][i] = float((1 - ALPHA) * old_p)
    # store update to mongodb, upsert: update and insert
    db[PREFERENCE_MODEL_TABLE_NAME].replace_one({'userId':userId}, model, upsert=True)


def run():
    #yizhi run
    while True:
        if cloudAMQP_client is not None:
            msg = cloudAMQP_client.getMessage()
            if msg is not None:
                try:
                    handle_message(msg)
                except Exception as e:
                    LOGGER.warn(e)
                    pass
        # Remove this if this becomes a bottleneck.
        cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)


if __name__ == "__main__":
    run()
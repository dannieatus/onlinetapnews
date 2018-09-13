#it's a tool to clear queue,/ manage queue, only for developer
import os
import sys

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from cloudAMQP_client import CloudAMQPClient

SCRAPE_NEWS_TASK_QUEUE_URL = "amqp://lmrfsaic:sgIlkcYxxRmhBXCltWGIOP8I8yqe5Cj5@otter.rmq.cloudamqp.com/lmrfsaic"
SCRAPE_NEWS_TASK_QUEUE_NAME = "tap-news-scarpe-news-task-queue"
DEDUPE_NEWS_TASK_QUEUE_URL = "amqp://tqrmlbso:y2iupCFv2tdZXpl4_wKfQlMXh13Zqug7@otter.rmq.cloudamqp.com/tqrmlbso"
DEDUPE_NEWS_TASK_QUEUE_NAME = "tap-news-dedupe-news-task-queue"

def clearQueue(queue_url, queue_name):
    queue_client = CloudAMQPClient(queue_url, queue_name)

    num_of_messages = 0
    # if news exist, fetch news continuously
    while True:
        if queue_client is not None:
            msg = queue_client.getMessage()
            if msg is None:
                print("Cleared %d messages." % num_of_messages)
                return
            num_of_messages += 1


if __name__ == "__main__":
    clearQueue(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)
    clearQueue(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
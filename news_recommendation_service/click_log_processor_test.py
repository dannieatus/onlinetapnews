import click_log_processor
import math
import os
import sys

from datetime import datetime

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client
#from mongodb
PREFERENCE_MODEL_TABLE_NAME = 'user_preference_model'
NEWS_TABLE_NAME = 'news'

NUM_OF_CLASSES = 8 

# Start MongoDB before running following tests.
def test_basic():
    db = mongodb_client.get_db()
    # delete previous test user
    db[PREFERENCE_MODEL_TABLE_NAME].delete_many({'userId': 'test_user'})
    # if mongodb has no newsId for test, so enter mongo->show dbs-> use demo -> show collections -> db.news.find().preggy()--> copy one digest 
    msg = {
        'userId':'test_user',
        'newsId':'3RjuEomJo26O1syZbU7OHA==\n',
        'timestamp':str(datetime.utcnow())
    }
    
    click_log_processor.handle_message(msg)
    
    # jiancha mongodb actually has a preference_model for test_user
    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId':'test_user'})
    assert model is not None
    assert len(model['preference']) == NUM_OF_CLASSES
    assert math.isclose(model['preference']['U.S.'], 0.2125, rel_tol=1e-10)

    print('test_basic passed!')

    
if __name__ == "__main__":
    test_basic()
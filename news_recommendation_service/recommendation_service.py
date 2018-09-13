""" Recommendation service """
# similar to backend_service/service.py
import logging
import math
import operator
import os
import sys

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

# import utils dir.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

import mongodb_client  # pylint: disable=import-error, wrong-import-position

PREFERENCE_MODEL_TABLE_NAME = 'user_preference_model'

SERVER_HOST = 'localhost'
SERVER_PORT = 5050

LOGGER_FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=LOGGER_FORMAT)
LOGGER = logging.getLogger('backend_server')
LOGGER.setLevel(logging.DEBUG)


def get_preference_for_user(user_id):
    """ Get user's preference in an sorted class list. """
    LOGGER.debug("get_preference_for_user is called with %s", str(user_id))
    db = mongodb_client.get_db()
    model = db[PREFERENCE_MODEL_TABLE_NAME].find_one({'userId':user_id})
    if model is None:
        return []
    """
    ('world', '0.124')
    ('us', 0.225)
    so use key=operator.itemgetter(1)
    reverse: higher is the starter, lower follows
    """
    sorted_tuples = sorted(list(model['preference'].items()), key=operator.itemgetter(1), reverse=True)
    # only use the first x[0]
    sorted_list = [x[0] for x in sorted_tuples]
    # panduan shibushi xiangdeng
    sorted_value_list = [x[1] for x in sorted_tuples]
    if math.isclose(float(sorted_value_list[0]), float(sorted_value_list[-1])):
        return []

    return sorted_list


# Threading RPC server.
RPC_SERVER = SimpleJSONRPCServer((SERVER_HOST, SERVER_PORT))
RPC_SERVER.register_function(get_preference_for_user, 'getPreferenceForUser')

LOGGER.info("Starting RPC server on %s:%d", SERVER_HOST, SERVER_PORT)

RPC_SERVER.serve_forever()
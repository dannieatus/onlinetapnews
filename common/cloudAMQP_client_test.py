from cloudAMQP_client import CloudAMQPClient

TEST_CLOUDAMQP_URL = "amqp://prtftooi:1m2TsGyueYdRZGtT0fH5xYI78k3H9DzZ@otter.rmq.cloudamqp.com/prtftooi"
TEST_QUEUE_NAME = "cs503"

def test_basic():
    client = CloudAMQPClient(TEST_CLOUDAMQP_URL, TEST_QUEUE_NAME)
    
    sentMsg = {'test':'123'}
    client.sendMessage(sentMsg)
    client.sleep(3)
    receivedMsg = client.getMessage()
    
    assert sentMsg == receivedMsg
    print('test_basic passed!')
    

if __name__ == '__main__':
    test_basic()
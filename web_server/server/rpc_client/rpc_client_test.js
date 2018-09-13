var client = require('./rpc_client');

client.add(1, 2, function(result) {
  // the response may be a string
  console.assert(result == 3)
})

// invoke 'getNewsSummariesForUser'
client.getNewsSummariesForUser('test_user', 1, function(response) {
   console.assert(response != null); 
});
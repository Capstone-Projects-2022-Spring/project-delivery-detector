import requests

def testGetUser(name):
    api = "http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/get_user/" + name + "/"
    # api = "http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/send_alert/" + name + "/" 
    apiResponse = requests.get(api)
    print (apiResponse)

#Tests for successful getUser functions
testGetUser("wifi_test")
testGetUser("test")
testGetUser("another_test")
testGetUser("testing")
testGetUser("aws")

#Tests for unsuccessful getUser functions
testGetUser("Luke")
testGetUser("Non-test")
testGetUser("Bug")
testGetUser("Temple")
testGetUser("University")

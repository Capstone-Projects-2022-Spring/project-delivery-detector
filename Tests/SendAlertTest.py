import requests

def testSendAlert(name, order_num):
    api = "http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/send_alert/" + name + "/" + order_num + "/" 
    apiResponse = requests.get(api)
    print (apiResponse)

#Tests for successful sendAlert functions

testSendAlert("brandon", "1")
testSendAlert("john", "1")
testSendAlert("abe", "2")
testSendAlert("lewis", "2")
testSendAlert("max", "2")

#Tests for unsuccessful getUser functions
testSendAlert("wach", "10")
testSendAlert("SERC", "6")
testSendAlert("Howard", "7")
testSendAlert("Cherry", "4")
testSendAlert("White", "2")
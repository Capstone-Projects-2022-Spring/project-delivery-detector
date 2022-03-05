import requests

# Example class for the client raspberry pi device
# The device will be making various API calls to the server 
class DeliveryDetectorBox():

    # Constructor 
    def __init__(self, box_num):
        self.box_number = box_num

    # Check if this box is registered to a specific user 
    def check_user_box(self, name):
        response = requests.get("http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/get_user/" + name + "/")
        res_obj = response.json()  
        if res_obj['box_number'] == self.box_number:
            print("UNLOCK THE BOX FOR USER: " + res_obj['user_name'])
        else:
            print('LOCK THE BOX')



if __name__ == '__main__':
    box = DeliveryDetectorBox(1)
    box.check_user_box('test')
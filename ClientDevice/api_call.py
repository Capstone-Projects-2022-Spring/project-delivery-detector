import requests

# Example class for the client raspberry pi device
# The device will be making various API calls to the server 
class DeliveryDetectorBox():

    # Constructor       
    def __init__(self, box_num):
        self.box_number = box_num

    # Check if this box is registered to a specific user 
    def check_user_box(self, name):
        # call the API 
        response = requests.get("http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/get_user/" + name + "/")
        res_obj = response.json()  

        # iterate through the JSON keys (database fields)
        for key in res_obj:
            print(str(key) + ': ' + str(res_obj[key]))

        # check if this is the correct box
        if res_obj['box_number'] == self.box_number:
            #unlock_box()
            print("UNLOCK THE BOX FOR USER: " + res_obj['user_name'])
        else:
            #lock_box()
            print('LOCK THE BOX')

    # Call the API endpoint for sending a alert 
    def send_alert(self, name):
        response = requests.get("http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/send_alert/" + name + "/")
        print(response.text)

    # Call the tamper API
    def send_tamper_alert(self, user_name, msg):
        response = requests.get("http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/tamper_alert/" + user_name + "/" + msg + '/')

    # Set up this box with all the users assigned to it
    # Returns a list of all users assigned to this box
    def get_all_assigned_users(self):
        # deploy the new endpoint and test with it 
        user_list = []
        response = requests.get("http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/get_all_users/" + str(self.box_number) + "/")
        res_obj = response.json()
        for key in res_obj:
            user_list.append(res_obj[key])
        return user_list

    # Returns a JSON object of all orders
    def get_all_assigned_orders(self):
        user_dict = {}
        response = requests.get("http://detector-env.eba-epj2ey8y.us-east-2.elasticbeanstalk.com/get_all_order_nums/")
        res_obj = response.json()
        for key in res_obj:
            user_dict.update({key: res_obj[key]})
        return user_dict

if __name__ == '__main__':
    # Create a new box DeliveryDetectorBox instance with box number 1
    box = DeliveryDetectorBox(1)
    box.check_user_box('test')  # the name will be found from the QR code reader

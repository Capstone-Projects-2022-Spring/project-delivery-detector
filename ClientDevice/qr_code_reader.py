# QR-Code reader for the raspberry pi client device
# Will use the OpenCV library to extract the QR-Code
# Will then use the extracted data to make an API call to the server
#
# Type 'sudo python3 qr_code_reader.py' to run this file  
# 
# ToDo
#   - need a way to load all order numbers on startup
#   - this is needeed if a package is already in the box, but the box reboots
#   - currently, the order numbers will be lost on each reboot
import cv2
import os, sys, stat
import time
import RPi.GPIO as GPIO
from api_call import DeliveryDetectorBox

buzz_pin = 40       # GPIO pin for the buzzer
user_slots = []     # list for user - ordernumber - slot dict 

# Extract the QR code 
def read_qr_code(multi_user=False, num_slots=0):
    vid = cv2.VideoCapture(0)
    box = DeliveryDetectorBox(1)
    frame_rate = 10     
    count = 0
    user_slots = {}
    if multi_user == True:
        user_slots = set_up_multi_box(box, num_slots)
    while (True):
        ret, image = vid.read()
        # Only extract the text after a certain number of frames
        if (count != 0) and (count % frame_rate) == 0:
            extract_text(image, box, user_slots)
            count = 0
        else:
            count += 1

# Extract the text from the QR code 
def extract_text(image, box, user_slots):
    qrCodeDetector = cv2.QRCodeDetector()
    decoded_text, points, _ = qrCodeDetector.detectAndDecode(image)
    if points is not None:
        print('Extracted ' + decoded_text + ' from the image')
        #cv2.imshow("Image", image)
        #cv2.waitKey(2000)
        if decoded_text != '':
            check_qr_text(box, decoded_text, user_slots)
        #cv2.destroyAllWindows()
    else:
        print("QR code not detected")

# Add the new WiFi to the config file 
def configWifi(text_list):
    network_name = text_list[1]
    network_password = text_list[2]
    os.chdir('/etc/wpa_supplicant/')
    f = open("wpa_supplicant.conf", "w")
    f.write("ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1" +
            '\ncountry=US\nnetwork={\n\tssid=\"' + network_name +
            '\"\n\tkey_mgmt=WPA-PSK\n\tpsk=\"' + network_password + '\"\n}')
    os.system('sudo shutdown -r now')

# Check the string embedded in the QR code 
def check_qr_text(box, text, user_slots):
    text_list = text.split('-')
    if len(text_list) > 1:
        if text_list[1] == '1':
            # package delivery
            box.check_user_box(text_list[0])
            box.send_alert(text_list[0])
            demo_buzz()
        elif (text_list[0] == 'wifi'):
            # WiFi hookup
            print("WiFi Hookup detected")
            configWifi(text_list)
            demo_buzz()
    else:
        # package pickup 
        box.check_user_box(text)
        demo_buzz()

# Deliver a package to a user assigned to a multi user box
def multi_user_deposite(list):
    user_name = list[0]
    order_number = list[1]
    for user in user_slots:
        if user_name == user['user_name']:
            # make a new API endpoint that multi-user client devices can use
            # this will send the slot number where the package is at 
            user_orders = user['order_numbers']
            # make sure this order is not currently waiting to be picked up by the box owner
            # if the order number is already in there, the package has already been dropped off
            for order in user_orders:
                if order_number == order:
                    # ERROR HERE
                    # the delivery person is trying to use the same QR code twice
                    # implement error logic
                    return
            user['order_numbers'].append(order_number)

def multi_user_pickup(list):
    user_name = list[0]
    order_number = list[1]
    for user in user_slots:
        if user_name == user['user_name']:
            user_orders = user['order_numbers']
            order_index = 0
            for order in user_orders:
                if order_number == order:
                    # unlock the box 
                    # reset the order number, will not work again 
                    # should make a new API endpoint to clear this order num
                    # this way, it wont be passed back
                    pass

def set_up_multi_box(box, num_slots):
    slot_index = 0
    all_users = box.get_all_assigned_users()
    all_orders = box.get_all_orders()
    user_order_dict = {}
    if len(all_users) > num_slots:
        # throw an error here and do not proceed
        # too many users are assigned to this box
        # need to implement error logic
        user_slots.append({'error': 'too many users assigned to this box'})
        pass

    # populate the order dict
    for order in all_orders.values():
        order_num = order[0]
        user_name = order[1]
        if user_name in all_users.keys():
            if user_name in user_order_dict.keys():
                user_order_dict[user_name] += order_num
            else:
                user_order_dict.update({user_name: order_num})

    # assign the users to slots and add valid order numbers
    for user in all_users:
        orders = user_order_dict[user] if user_order_dict[user] is not None else -1 
        user_slots.append({'user_name': user, 'order_numbers': orders, 'slot': slot_index})
        slot_index += 1

    return user_slots



# Run the buzzer for demo purposes 
def demo_buzz():
    GPIO.output(buzz_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(buzz_pin, GPIO.LOW)

# Check if this script is being run directly 
if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buzz_pin, GPIO.OUT)
    demo_buzz()
    read_qr_code()




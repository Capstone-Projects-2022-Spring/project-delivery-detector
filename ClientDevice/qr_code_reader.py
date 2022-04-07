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
#   - REFACTOR
#import cv2
import os, sys, stat
import time
import RPi.GPIO as GPIO
from api_call import DeliveryDetectorBox

buzz_pin = 40       # GPIO pin for the buzzer
user_slots = []     # list for user - ordernumber - slot dict 

# Extract the QR code 
def read_qr_code(num_slots=1):
    vid = cv2.VideoCapture(0)
    box = DeliveryDetectorBox(1)
    frame_rate = 10     
    count = 0
    set_up_multi_box(box, num_slots) if num_slots > 1 else set_up_single_box(box)
    while (True):
        ret, image = vid.read()
        # Only extract the text after a certain number of frames
        if (count != 0) and (count % frame_rate) == 0:
            extract_text(image, box, user_slots)
            count = 0
        else:
            count += 1

def set_up_single_box(box):
    all_users = box.get_all_assigned_users()
    all_orders = box.get_all_assigned_orders()
    user = all_users[0] 
    orders = []
    for order in all_orders.values():
        order_num = order[0]
        user_name = order[1]
        # check if the user is assigned to this box
        if user_name == user:
            # check if this user is already in the order dict
            orders.append(order_num)
    # need to make sure the slot numbers dont have conflicts 
    user_slots.append({'user_name': user, 'order_numbers': orders, 'slot': -1})

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
# QR code is embedded as follows:
#   name-ordernumber-packagetype
#   packagetype:
#       1 = delivery
#       0 = pickup
def check_qr_text(box, text, user_slots):
    text_list = text.split('-')
    user_name = text_list[0]
    order_num = text_list[1]
    package_type = text_list[2]
    # check for a mutli-user box 
    if (len(user_slots) > 1):
        check_qr_multi_user(box, text_list)
        return
    if (package_type == '1'):
        # package delivery
        package_delivery(box, user_name, order_num)
    elif (package_type == '0'):
        # package pickup 
        package_pickup(box, user_name, order_num)
    elif (text_list[0] == 'wifi'):
        # WiFi hookup
        print("WiFi Hookup detected")
        configWifi(text_list)
        demo_buzz()

def check_qr_multi_user(box, text_list):
    # text_list = [name, order-number, dropoff or pickup]
    user_name = text_list[0]
    order_num = text_list[1]
    package_type = text_list[2]
    if (package_type == 1):
        package_deposite(box, user_name, order_number)
    elif (package_type == 0):
        package_pickup(box, user_name, order_number)

# Deliver a package to a user assigned to a multi user box
def package_delivery(box, user_name, order_number):
    if bad_order_num(user_name, order_number): return
    for user in user_slots:
        if user_name == user['user_name']:
            user_orders = user['order_numbers']
            # make sure this order is not currently waiting to be picked up by the box owner
            # if the order number is already in there, the package has already been dropped off
            for order in user_orders:
                if order_number == order:
                    # the delivery person is trying to use the same QR code twice
                    print("\nERROR - DELIVRY PERSON RE-USING THE QR CODE!!\n")
                    return
            # add the order to the user's list of order numbers
            # send the alert
            box.send_alert(user_name, order_number, user['slot'])
            user['order_numbers'].append(order_number)
            #demo_buzz()
            return

# Pick up a package to a user assigned to a multi user box
def package_pickup(box, user_name, order_number):
    for user in user_slots:
        if user_name == user['user_name']:
            user_orders = user['order_numbers']
            for order in user_orders:
                if order_number == order:
                    # unlock the box
                    print("UNLOCK THE BOX")
                    #demo_buzz()
                    return

# Configure the box and the device to work for multiple users
def set_up_multi_box(box, num_slots):
    slot_index = 0
    all_users = box.get_all_assigned_users()
    all_orders = box.get_all_assigned_orders()
    user_order_dict = {}
    if len(all_users) > num_slots:
        # throw an error here and do not proceed
        # too many users are assigned to this box
        # need to implement error logic
        user_slots.append({'error': 'too many users assigned to this box'})
        return 

    # populate the order dict
    for order in all_orders.values():
        order_num = order[0]
        user_name = order[1]
        # check if the user is assigned to this box
        if user_name in all_users:
            # check if this user is already in the order dict
            if user_name in user_order_dict.keys():
                user_order_dict[user_name].append(order_num)
            else:
                user_order_dict.update({user_name: [order_num]})

    # assign the users to slots and add valid order numbers
    for user in all_users:
        orders = user_order_dict[user] if user in user_order_dict.keys() else -1 
        user_slots.append({'user_name': user, 'order_numbers': orders, 'slot': slot_index})
        slot_index += 1

# Run the buzzer for demo purposes 
def demo_buzz():
    GPIO.output(buzz_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(buzz_pin, GPIO.LOW)

def test_box():
    # go through work-flow of the following, with the secure QR:
    #   (1) Delivery Person dropping off for multiple users
    #       Box owner comes and pick its up
    #
    #   (2) Delivery Person dropping off for single
    #       Box owner comes and pick its up

    # multiple user
    box = DeliveryDetectorBox(1)
    set_up_multi_box(box, 9)
    print(user_slots)
    name = 'test3'
    order_num = 1111111111
    package_delivery(box, name, order_num)
    time.sleep(5)
    print(user_slots)
    package_pickup(box, name, order_num)
    print('packaged pick up ')

    """
        # single user
        box = DeliveryDetectorBox(2)
        set_up_single_box(box)
        print(user_slots)
        name = 'johng'
        order_num = 2222676111
        package_delivery(box, name, order_num)
        time.sleep(5)
        print(user_slots)
        package_pickup(box, name, order_num)
        print('packaged pick up ')
    """


# Check if this script is being run directly 
if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buzz_pin, GPIO.OUT)
    demo_buzz()
    test_box()
    #read_qr_code()
    #read_qr_code(4)




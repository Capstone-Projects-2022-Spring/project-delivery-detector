# QR-Code reader for the raspberry pi client device
# Will use the OpenCV library to extract the QR-Code
# Will then use the extracted data to make an API call to the server
#
# This program will be run on boot by the client device 
#
# Type 'sudo python3 qr_code_reader.py' to run this file directly 
import cv2
import os, sys, stat
import time
import threading
import RPi.GPIO as GPIO
from api_call import DeliveryDetectorBox
from adxl import run_adxl

buzz_pin = 21       # GPIO pin for the buzzer
led_green_pin = 16  # GPIO pin for green LED
led_red_pin = 20    # GPIO pin for red LED
user_slots = []     # list for user - ordernumber - slot dict 

# Extract the QR code 
def read_qr_code(box_num, num_slots=1):
    vid = cv2.VideoCapture(0)
    box = DeliveryDetectorBox(box_num)
    frame_rate = 10     
    count = 0
    set_up_multi_box(box, num_slots) if num_slots > 1 else set_up_single_box(box)
    sensor_thread = sensor_thread_init(box_num)
    sensor_thread.start()
    while (True):
        ret, image = vid.read()
        # Only extract the text after a certain number of frames
        if (count != 0) and (count % frame_rate) == 0:
            extract_text(image, box)
            count = 0
        else:
            count += 1

def sensor_thread_init(box_num):
    names = user_slots.keys()
    thread = threading.Thread(target=run_adxl, args=(box_num, names))
    return thread 

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
def extract_text(image, box):
    qrCodeDetector = cv2.QRCodeDetector()
    decoded_text, points, _ = qrCodeDetector.detectAndDecode(image)
    if points is not None:
        print('Extracted ' + decoded_text + ' from the image')
        #cv2.imshow("Image", image)
        #cv2.waitKey(2000)
        if decoded_text != '':
            check_qr_text(box, decoded_text)
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
def check_qr_text(box, text):
    text_list = text.split('-')
    if (len(text_list) == 3):
        user_name = text_list[0]
        order_num = text_list[1]
        package_type = text_list[2]
    else:
        return
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
    if (len(text_list) == 3):
        user_name = text_list[0]
        order_num = text_list[1]
        package_type = text_list[2]
        if (package_type == '1'):
            package_delivery(box, user_name, order_num)
        elif (package_type == '0'):
            package_pickup(box, user_name, order_num)

# Deliver a package to a user assigned to a multi user box
def package_delivery(box, user_name, order_number):
    if box.bad_order_num(user_name, order_number): 
        print('ERROR: ORDER NUMBER ' + str(order_number) + ' IS NOT VALID')
        return
    for user in user_slots:
        if user_name == user['user_name']:
            user_orders = user['order_numbers']
            # make sure this order is not currently waiting to be picked up by the box owner
            # if the order number is already in there, the package has already been dropped off
            for order in user_orders:
                print('checking ' + str(order_number) + ' and ' + str(order))
                if int(order_number) == int(order):
                    # the delivery person is trying to use the same QR code twice
                    print('ERROR - DELIVERY PERSON')
                    box.send_tamper_alert(user_name, 'qr')
                    return
            # add the order to the user's list of order numbers
            # send the alert
            box.send_alert(user_name, order_number, user['slot'])
            user['order_numbers'].append(order_number)
            led_green_light()
            led_red_light()
            return

# Pick up a package to a user assigned to a multi user box
def package_pickup(box, user_name, order_number):
    for user in user_slots:
        if user_name == user['user_name']:
            if not box.bad_order_num(user_name, order_number):
                # unlock the box
                print("UNLOCK THE BOX")
                led_green_light()
                led_red_light()
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
    print(user_slots)

# Turn on the green LED on and the red LED off
def led_green_light():
    GPIO.output(led_green_pin, GPIO.HIGH)
    GPIO.output(led_red_pin, GPIO.LOW)
    time.sleep(20)

# Turn on the red LED
def led_red_light():
    GPIO.output(led_red_pin, GPIO.HIGH)
    GPIO.output(led_green_pin, GPIO.LOW)

# Run the buzzer for demo purposes 
def demo_buzz():
    GPIO.output(buzz_pin, GPIO.HIGH)
    GPIO.output(led_red_pin, GPIO.HIGH)
    GPIO.output(led_green_pin, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(led_green_pin, GPIO.LOW)
    GPIO.output(buzz_pin, GPIO.LOW)

# go through work-flow of the following, with the secure QR:
#   (1) Delivery Person dropping off for multiple users
#       Box owner comes and pick its up
#
#   (2) Delivery Person dropping off for single
#       Box owner comes and pick its up
def test_box():
    # multiple user
    box = DeliveryDetectorBox(1)
    set_up_multi_box(box, 9)
    print(user_slots)
    """
    name = 'test3'
    order_num = 1111111111
    package_delivery(box, name, order_num)
    time.sleep(5)
    print(user_slots)
    package_pickup(box, name, order_num)
    print('package picked up ')
    """
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

def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_green_pin, GPIO.OUT)
    GPIO.setup(led_red_pin, GPIO.OUT)
    GPIO.setup(buzz_pin, GPIO.OUT)


# Check if this script is being run directly 
if __name__ == '__main__':
    gpio_init()
    demo_buzz()
    #test_box()
    #read_qr_code(box_num2)
    read_qr_code(box_num=1, num_slots=9) 


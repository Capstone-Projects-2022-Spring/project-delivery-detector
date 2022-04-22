import cv2
import os, sys, stat
import time
import threading
import RPi.GPIO as GPIO
from api_call import DeliveryDetectorBox
from servo_firmware import DetectorServos
from adxl import run_adxl

# Main class for the Delivery Detector client device 
class DetectorClient():

    # Constructor for the device
    def __init__(self, box_num, buzz_pin=21, green_pin=16, red_pin=20, num_slots=1):
        self.buzz_pin = 21
        self.led_green_pin = green_pin
        self.led_red_pin = red_pin
        self.num_slots = num_slots
        self.box_num = box_num
        self.frame_rate = 10
        self.user_slots = []                
        self.box = DeliveryDetectorBox(box_num)
        self.detector_servos = DetectorServos()


    # Run the main client detector logic 
    def run(self):
        self.detector_init()
        self.demo_buzz()
        self.read_qr_code() 


    # Initiliaze the GPIO pins 
    def detector_init(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_green_pin, GPIO.OUT)
        GPIO.setup(self.led_red_pin, GPIO.OUT)
        GPIO.setup(self.buzz_pin, GPIO.OUT)
        self.init_box(self) 
        self.detector_servos.set_num_servos(len(self.user_slots))
        self.detector_servos.init_servos()
        #sensor_thread = sensor_thread_init()
        #sensor_thread.start()


    # Extract the QR code 
    def read_qr_code(self):
        vid = cv2.VideoCapture(0)
        frame_rate = 10     
        count = 0
        while (True):
            ret, image = vid.read()
            # Only extract the text after a certain number of frames
            if (count != 0) and (count % self.frame_rate) == 0:
                self.extract_text(image)
                count = 0
            else:
                count += 1


    # Intiliaze the ADXL-345 sensor thread
    def sensor_thread_init(self):
        names = self.user_slots.keys()
        thread = threading.Thread(target=run_adxl, args=(self.box_num, names))
        return thread 


    # Extract the text from the QR code 
    def extract_text(self, image):
        qrCodeDetector = cv2.QRCodeDetector()
        decoded_text, points, _ = qrCodeDetector.detectAndDecode(image)
        if points is not None:
            print('Extracted ' + decoded_text + ' from the image')
            #cv2.imshow("Image", image)
            #cv2.waitKey(2000)
            if decoded_text != '':
                self.check_qr_text(decoded_text)
            #cv2.destroyAllWindows()
        else:
            print("QR code not detected")


    # Add the new WiFi to the config file 
    def configWifi(self, text_list):
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
    def check_qr_text(self, text):
        text_list = text.split('-')
        if (len(text_list) != 3): return
        user_name = text_list[0]
        order_num = text_list[1]
        package_type = text_list[2]
        if (package_type == '1'):
            # package delivery
            self.package_delivery(user_name, order_num)
        elif (package_type == '0'):
            # package pickup 
            self.package_pickup(user_name, order_num)
        elif (text_list[0] == 'wifi'):
            # WiFi hookup
            print("WiFi Hookup detected")
            self.configWifi(text_list)
            self.demo_buzz()


    # Deliver a package to a user assigned to a multi user box
    def package_delivery(self, user_name, order_number):
        if self.box.bad_order_num(user_name, order_number): 
            print('ERROR: ORDER NUMBER ' + str(order_number) + ' IS NOT VALID')
            self.box.send_tamper_alert(user_name, 'qr')
            return
        else:
            for user in self.user_slots:
                if user['user_name'] == user_name:
                    if is_old_qr_code(user, order_number): return
                    self.box.send_alert(user_name, order_number, user['slot'])
                    user['order_numbers'].append(order_number)
                    self.led_green_light()
                    self.detector_servos.unlock_slot_door(int(user['slot']))
                    self.detector_servos.lock_slot_door(int(user['slot']))
                    self.led_red_light()

    
    # Check if a QR code is being used twice by a delivery person
    def is_old_qr_code(self, user, order_number):
        for order in user['order_numbers']:
            if int(order_number) == int(order):
                print('ERROR - DELIVERY PERSON')
                box.send_tamper_alert(user_name, 'qr')
                flash_red_leds(5)
                return True
        return False


    # Pick up a package to a user assigned to a multi user box
    def package_pickup(self, user_name, order_number):
        for user in self.user_slots:
            if user_name == user['user_name']:
                if not box.bad_order_num(user_name, order_number):
                    # unlock the box
                    print("UNLOCK THE BOX")
                    self.led_green_light()
                    self.detector_servos.unlock_slot_door(int(user['slot']))
                    self.detector_servos.lock_slot_door(int(user['slot']))
                    self.led_red_light()
                    return


    # Configure the box and the device to work for multiple users
    def init_box(self):
        slot_index = 0
        all_users = self.box.get_all_assigned_users()
        all_orders = self.box.get_all_assigned_orders()
        user_order_dict  = {}
        if len(all_users) > self.num_slots:
            # throw an error here and do not proceed
            # too many users are assigned to this box
            # need to implement error logic
            # maybe flash red LEDS?
            self.user_slots.append({'error': 'too many users assigned to this box'})
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
            self.user_slots.append({'user_name': user, 'order_numbers': orders, 'slot': slot_index})
            slot_index += 1
    

    # Turn on the green LED on and the red LED off
    def led_green_light(self):
        GPIO.output(self.led_green_pin, GPIO.HIGH)
        GPIO.output(self.led_red_pin, GPIO.LOW)
        time.sleep(2)


    # Turn on the red LED
    def led_red_light(self):
        GPIO.output(self.led_red_pin, GPIO.HIGH)
        GPIO.output(self.led_green_pin, GPIO.LOW)


    # Flash the red LEDs
    def flash_red_leds(num):
        GPIO.output(self.led_green_pin, GPIO.LOW)
        for i in range(num):
            GPIO.output(self.led_red_pin, GPIO.HIGH)
            time.sleep(4)
            GPIO.output(self.led_red_pin, GPIO.HIGH)
            time.sleep(2)


    # Run the buzzer for demo purposes 
    def demo_buzz(self):
        GPIO.output(self.buzz_pin, GPIO.HIGH)
        GPIO.output(self.led_red_pin, GPIO.HIGH)
        GPIO.output(self.led_green_pin, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(self.led_green_pin, GPIO.LOW)
        GPIO.output(self.buzz_pin, GPIO.LOW)
    


# Check if this script is being run directly
if __name__ == 'main':
    detector_client = DetectorClient(box_num=1, num_slots=9)
    detector_client.run()
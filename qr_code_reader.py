# Type 'sudo python3 qr_code_reader.py' to run this file  
import cv2
import os, sys, stat
import time
import RPi.GPIO as GPIO
from api_call import DeliveryDetectorBox



# QR-Code reader for the raspberry pi client device
# Will use the OpenCV library to extract the QR-Code
# Will then use the extracted data to make an API call to the server

buzz_pin = 40

# Extract the QR code 
def read_qr_code():
    vid = cv2.VideoCapture(0)
    box = DeliveryDetectorBox(1)
    while (True):
        ret, image = vid.read()
        qrCodeDetector = cv2.QRCodeDetector()
        decoded_text, points, _ = qrCodeDetector.detectAndDecode(image)
        if points is not None:
            print('Extracted ' + decoded_text + ' from the image')
            cv2.imshow("Image", image)
            cv2.waitKey(2000)
            if decoded_text != '':
                check_qr_text(box, decoded_text)
            cv2.destroyAllWindows()
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
def check_qr_text(box, text):
    text_list = text.split('-')
    if len(text_list) > 1:
        if text_list[1] == '1':
            # package delivery
            box.check_user_box(text_list[0])
            box.send_alert(text_list[0])
            demo_buzz()
        elif (text_list[1] == 'wifi'):
            # WiFi hookup
            print("WiFi Hookup detected")
            configWifi(text_list)
            demo_buzz()
    else:
        # package pickup 
        box.check_user_box(text)
        demo_buzz()

# Run the buzzer for demo purposes 
def demo_buzz():
    GPIO.out(buzz_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.out(buzz_pin, GPIO.LOW)

# Check if this script is being run directly 
if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buzz_pin, GPIO.OUT)
    demo_buzz()
    read_qr_code()

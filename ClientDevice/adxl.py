# ADXL-345 program for the client device
# Will act as an anti-tampering sensor
import time
import board
import busio
import adafruit_adxl34x
from api_call import DeliveryDetectorBox

def run_adxl(box_num, names):
    box = DeliveryDetectorBox(box_num)
    i2c = busio.I2C(board.SCL, board.SDA)
    adxl = adafruit_adxl34x.ADXL345(i2c)
    adxl.enable_motion_detection(threshold=18)
    while True:
        val = adxl.events['motion']
        if (val == True):
            # send an alert to each user assigned to the box
            for name in names:
                box.send_tamper_alert(name, 'move')
        time.sleep(0.5)


if __name__ == '__main__':
    box = DeliveryDetectorBox(1)
    run_adxl(box, ['johng'])

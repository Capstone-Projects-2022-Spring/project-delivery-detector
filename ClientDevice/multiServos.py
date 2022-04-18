# Build instructions
# sudo pip3 install adafruit-circuitpython-pca9685
# sudo pip3 install adafruit-circuitpython-motor
# Enable I2C in preferences -> Raspberry Configurations -> Interfaces
# or through command line $sudo raspi-config -> Interface Options 
#
# Servo board must be connected to GPIO 2 (SDA), GPIO 3(SCL) , 3v3 Power (pin 1 or 17) and ground


import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

all_servos = []
servo0 = servo.Servo(pca.channels[0])
servo1 = servo.Servo(pca.channels[1])
servo2 = servo.Servo(pca.channels[2])


def lock(servo):
    servo.fraction = .55
    time.sleep(.03)

def unlock(servo):
    servo.fraction = 0
    time.sleep(.03)


if __name__ == "__main__":
    unlock(servo0)
    unlock(servo1)
    unlock(servo2)
    time.sleep(2)
    print("unlocked")
    lock(servo0)
    lock(servo1)
    lock(servo2)
    print("Locked")

    pca.deinit()
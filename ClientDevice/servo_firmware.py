import busio
import time
from adafruit_servokit import ServoKit


class DetectorServos():

    # Constrcutor for the DetectorServer
    def __init__(self, num_servos=1):
        self.num_servos = num_servos
        self.servos = ServoKit(channels=16)
        
    # Set the number of servos connected to the driver
    # Can be used by the client device when initalizing
    def set_num_servos(self, num_servos):
        if num_servos > 0:
            self.num_servos = num_servos


    # Send all the servos back home 
    def home_all_servos(self):
        for i in range(self.num_servos):
            self.servos.servo[i].angle = 0
        time.sleep(2)


    # Move all the servos 180 degrees
    def move_all_servos(self):
        for i in range(self.num_servos):
            self.servos.servo[i].angle = 180
        time.sleep(2)


    # Move a specfic servo, unlocking a door
    def move_slot_door(self, slot_number, angle):
        if slot_number >= self.num_servos:
            return
        self.servos.servo[slot_number].angle = angle
        time.sleep(5)


    # Lock a slot door 
    def lock_slot_door(self, slot_number):
        if slot_number >= self.num_servos:
            return
        self.servos.servo[slot_number].angle = 0


    # Lock a slot door 
    def unlock_slot_door(self, slot_number):
        if slot_number >= self.num_servos:
            return
        self.servos.servo[slot_number].angle = 180
        time.sleep(5)


    # Initliaze the servos
    def init_servos(self):
        self.home_all_servos()
        self.move_all_servos()
        self.home_all_servos()


if __name__ == '__main__':
    detector_servos = DetectorServos(3)
    detector_servos.init_servos()
    detector_servos.move_slot_door(0, 180)
    detector_servos.move_slot_door(0, 0)

import serial 
import time 

class CarControl:
    def __init__(self, device):
        self.arduino_device = device
        self.ser = serial.Serial(self.arduino_device, 9600)
        time.sleep(2)

    def move(self, direction, speed): 
        self.ser.write(int(direction).to_bytes(1, 'big'))
        self.ser.write(int(speed).to_bytes(1, 'big')) #от 0 до 255
        time.sleep(0.0002)

    def turn(self, degree):
        self.ser.write(int(3).to_bytes(1, 'big'))
        self.ser.write(int(degree).to_bytes(1, 'big'))
        time.sleep(0.0002)
    
    def getDistance(self):
        dists = [None, None, None];

        self.ser.write(int(4).to_bytes(1, 'big'))
        self.ser.write(int(0).to_bytes(1, 'big'))

        for i in range(0, 3):
            time.sleep(0.0002)
            sonic_id = int.from_bytes(self.ser.read(), 'big')
            sonic_dist = int.from_bytes(self.ser.read(), 'big')

            if sonic_dist > 0 and sonic_dist < 30:
                dists[sonic_id] = sonic_dist

        return dists

    def portDBG(self):
        print(self.ser.readline())

    def __del__(self):
        self.ser.close()

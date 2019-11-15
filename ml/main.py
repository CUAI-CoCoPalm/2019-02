import smbus			#import SMBus module of I2C
from time import sleep          #import
from datetime import datetime
import argparse
import pickle
import os
import numpy as np
import lightgbm as lgb
import pandas as pd

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

bus = smbus.SMBus(1)
# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

def MPU_Init():
    #write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
    #Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
    #Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)
	
    #Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
    #Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)
    print ("Initalized GPIO!")
    print ()


def read_raw_data(addr):
    #Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)
    
    #concatenate higher and lower value
    value = ((high << 8) | low)
        
    #to get signed value from mpu6050
    if(value > 32768):
        value = value - 65536
    return value


def record():
	
    #Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)
	
    #Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)
	
    #Full scale range +/- 250 degree/C as per sensitivity scale factor
    Ax = acc_x/16384.0
    Ay = acc_y/16384.0
    Az = acc_z/16384.0
	
    Gx = gyro_x/131.0
    Gy = gyro_y/131.0
    Gz = gyro_z/131.0

    record = [round(Gx,4),  round(Gy,4), round(Gz,4),  round(Ax,4), round(Ay,4), round(Az, 4)]

    sleep(0.05)
    return record

def get_motion_name(m_id):

    if m_id == 0:
        motion = 'up2down'
    elif m_id == 1:
        motion = 'right2left'
    elif m_id == 2:
        motion = 'left2right'
    elif m_id == 3:
        motion = 'clockwise'
    elif m_id == 4:
        motion = 'cClockwise'

    return motion

def isAllZero(line):
    for element in line:
        if float(element) != 0.0:
            return False

    return True
    
if __name__ == '__main__':
    MPU_Init()
    bundle = []

    with open('./model/lightGBM.txt', 'rb') as f:
        models = pickle.load(f)

    print ("Do")
    print ()

    try:
        total = 0
        while True:
            line = record()

            if isAllZero(line):
                print ("Line Error! Check Again!")
                print ("Press any key to continue")
                isError = True
                ch = input()

            bundle.extend(line)

            if total > 16:
                bundle.pop(0)
                wrapper = []
                wrapper.append(bundle)

                predictions = []

                for model in models:
                    prediction = model.predict(wrapper, num_iteration=model.best_iteration)
                    predictions.append(prediction)

                predictions = np.mean(predictions, axis=0)

                result = np.argmax(predictions, axis=1)

                if max(predictions[0]) > 0.9:
                    motion = get_motion_name(result)
                    print ("Motion Detect: ", motion, " |", round(max(predictions[0]), 4))
                    print ()
                    bundle = bundle[4:]
            else:
                total += 1           

    except Exception as e:
        print ("Error:", e)

#!/usr/bin/python

# import lirc
import pylirc
import time
import RPi.GPIO as GPIO
import sys
import os
import logging
from datetime import datetime
from Adafruit_PWM_Servo_Driver import PWM
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
#import QR_r
import time

current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

PWMA = 18
AIN1 = 27
AIN2 = 22

PWMB = 23
BIN1 = 24
BIN2 = 25

BtnPin = 19
Gpin = 5
Rpin = 6

blocking = 0
CANCEL = 14
LED = 11
L_Motor = 0
R_Motor = 0

# 舵机云台控制引脚定义
pwm = PWM(0x40, debug=False)
pwm.setPWMFreq(50)  # Set frequency to 60 Hz
# pwm.setPWM(0,0,153)

SERVO_VERTICAL_CHANNEL = 1  # 水平方向舵机控制引脚
SERVO_HORIZONTAL_CHANNEL = 2  # 垂直方向舵机控制引脚

yaw_vertical = 0  # 垂直方向初始角度
yaw_horizontal = 90  # 水平方向初始角度

# 电机初始速度
cur_speed = 50

# 控制拍照的标志
flag = 0
number_photo = 1
cv2.namedWindow("Photo_Detect")


def log():
    log_path = '/home/pi/Desktop/LCDMenu/Logs/'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                        datefmt='%a %d %b %Y %H:%M:%S',
                        filename=log_path + 'remote control: ' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.log',
                        filemode='w')

    

# Set PWM
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000.0  # 1,000,000 us per second
    pulse_length /= 50.0  # 60 Hz
    print("%d us per period" % pulse_length)
    pulse_length /= 4096.0  # 12 bits of resolution
    print("%d us per bit" % pulse_length)
    pulse *= 1000.0
    pulse /= (pulse_length * 1.0)
    # pwmV=int(pulse)
    print("pulse: %f  " % pulse)

    pwm.setPWM(channel, 0, int(pulse))  # 2


# Angle to PWM
def write_camera_servo(channel, x):
    y = x / 90.0 + 0.5
    y = max(y, 0.5)
    y = min(y, 2.5)
    set_servo_pulse(channel, y)  # 2


def t_up(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, False)  # AIN2
    GPIO.output(AIN1, True)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, True)  # BIN1
    time.sleep(t_time)


def t_stop(t_time):
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(AIN2, False)  # AIN2
    GPIO.output(AIN1, False)  # AIN1

    R_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, False)  # BIN1
    time.sleep(t_time)


def t_down(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, True)  # AIN2
    GPIO.output(AIN1, False)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, True)  # BIN2
    GPIO.output(BIN1, False)  # BIN1
    time.sleep(t_time)


def t_left(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, True)  # AIN2
    GPIO.output(AIN1, False)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, True)  # BIN1
    time.sleep(t_time)
    t_stop(0)


def t_right(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, False)  # AIN2
    GPIO.output(AIN1, True)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, True)  # BIN2
    GPIO.output(BIN1, False)  # BIN1
    time.sleep(t_time)
    t_stop(0)


def keysacn():
    val = GPIO.input(BtnPin)
    while GPIO.input(BtnPin) == False:
        val = GPIO.input(BtnPin)
    while GPIO.input(BtnPin) == True:
        time.sleep(0.01)
        val = GPIO.input(BtnPin)
        if val == True:
            GPIO.output(Rpin, 1)
            while GPIO.input(BtnPin) == False:
                GPIO.output(Rpin, 0)
        else:
            GPIO.output(Rpin, 0)


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(PWMA, GPIO.OUT)

    GPIO.setup(BIN1, GPIO.OUT)
    GPIO.setup(BIN2, GPIO.OUT)
    GPIO.setup(PWMB, GPIO.OUT)
    GPIO.setup(Rpin, GPIO.OUT)  # Set Red Led Pin mode to output
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(CANCEL, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(LED, GPIO.OUT)


def screenshot(src):
    global number_photo
    new_folder = '/home/pi/Desktop/LCDMenu/Photos/'
    os.makedirs(new_folder, exist_ok=True)
    save_path = os.path.join(new_folder, 'remote control: ' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + "-" + str(
        number_photo) + ' Picture.jpg')
    cv2.imwrite(save_path, src)
    # cv2.imwrite(str(number_photo) +' QR code.jpg', result)
    # number_photo = number_photo + 1


def save_photo(src, roi):
    global number_photo
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)
    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        if barcodeData != "":
            result = np.copy(roi)
            print(current_time + '-'+ 'number_photo'+"qrcode : %s" % barcodeData)
            cv2.putText(result, "qrcode:" + str(barcodeData), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                        2)
            cv2.putText(result, str(number_photo) + ' QR code', (800, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
            stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # print(number_photo)
            new_folder = '/home/pi/Desktop/LCDMenu/Photos/'
            os.makedirs(new_folder, exist_ok=True)
            save_path = os.path.join(new_folder, 'remote control' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + " " + str(
                number_photo) + ' QR code.jpg')
            cv2.imwrite(save_path, src)
            # cv2.imwrite(str(number_photo) +' QR code.jpg', result)
            number_photo = number_photo + 1


def IR(config, src, roi):
    global yaw_vertical, yaw_horizontal, cur_speed
    global flag

    # camera_test.take_screenshot(flag)
    if config == 'KEY_CHANNEL':
        t_up(cur_speed, 0)
        print(current_time + '-'+'Move forwards')
        logging.info("Move forward")
    if config == 'KEY_VOLUMEUP':
        t_down(cur_speed, 0)
        print(current_time + '-'+'Move backwards')
        logging.info("Move backwards")
    if config == 'KEY_NEXT':
        t_stop(0)
        print(current_time + '-'+'Emergency stop')
        logging.info("Emergency stop")
    if config == 'KEY_PREVIOUS':
        t_left(cur_speed, 0.42)
        print(current_time + '-'+'Turn left')
        logging.info("Turn left")
    if config == 'KEY_PLAYPAUSE':
        t_right(cur_speed, 0.42)
        print(current_time + '-'+'Turn right')
        logging.info("Turn right")
    if config == 'KEY_EQUAL':
        cur_speed = cur_speed + 20
        print('Increase speed, current speed is ', cur_speed)
        logging.info('Increase speed, current speed is ', cur_speed)
    if config == 'KEY_VOLUMEDOWN':
        cur_speed = cur_speed - 20
        print('Decrease speed, current speed is ', cur_speed)
        logging.info('Decrease speed, current speed is ', cur_speed)
    if config == 'KEY_NUMERIC_2':
        # move_camera('up')
        yaw_vertical = yaw_vertical - 5
        write_camera_servo(2, yaw_vertical)
        time.sleep(0.5)
        print(current_time + '-'+'Tilt camera up')
        logging.info(current_time + '-'+'Tilt camera up')
    if config == 'KEY_NUMERIC_8':
        # move_camera('down')
        yaw_vertical = yaw_vertical + 5
        write_camera_servo(2, yaw_vertical)
        time.sleep(0.5)
        print(current_time + '-'+'Tilt camera down')
        logging.info(current_time + '-'+'Tilt camera down')
    if config == 'KEY_NUMERIC_4':
        # move_camera('left')
        yaw_horizontal = yaw_horizontal + 5
        write_camera_servo(1, yaw_horizontal)
        # write_camera_servo(1, 145)
        time.sleep(0.5)
        print(current_time + '-'+'Tilt camera left')
        logging.info(current_time + '-'+'Tilt camera left')
    if config == 'KEY_NUMERIC_6':
        # move_camera('right')
        yaw_horizontal = yaw_horizontal - 5
        write_camera_servo(1, yaw_horizontal)
        # write_camera_servo(1, 5)
        time.sleep(0.5)
        print(current_time + '-'+'Tilt camera right')
        logging.info(current_time + '-'+'Tilt camera right')
    if config == 'KEY_NUMERIC_5':
        # flag = 1
        # QR_r.take_screenshot()
        # camera_test.take_screenshot()

        # 直接拍照
        screenshot(src)

        # 识别二维码
        # save_photo(src, roi)

        # flag = 0
        # QR_r.log()
        print('Take picture')
        logging.info("Take picture")


def take_camera(flag):
    global number_photo
    cap = cv2.VideoCapture(0)

    while True:

        ret, src = cap.read()

        if not ret:
            break

        cv2.imshow('Photo_Detect', src)

        height, width = src.shape[:2]
        center_x = int(width / 2)
        center_y = int(height / 2)
        roi_size = 250
        roi_left = center_x - int(roi_size / 2)
        roi_top = center_y - int(roi_size / 2)
        roi_right = center_x + int(roi_size / 2)
        roi_bottom = center_y + int(roi_size / 2)
        roi = src[roi_top:roi_bottom, roi_left:roi_right]
        cv2.imshow('center', roi)

        # save_photo(src, roi)
        # loop(src, roi)
        s = pylirc.nextcode(1)

        while (s):
            for (code) in s:
                print(current_time + '-'+'Command: ', code["config"])
                # take_camera(code["config"])
                IR(code["config"], src, roi)
                if flag == 'extensive':
                    logging.info(current_time + '-'+'Command: ', code["config"])
            if (not blocking):
                s = pylirc.nextcode(1)
                # s = lirc.nextcode(1)
            else:
                s = []

        # if number_photo == 2:
        #     number_photo = 1
        #     break

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
        if GPIO.input(CANCEL) == 0:
            GPIO.cleanup()
            L_Motor = 0
            R_Motor = 0

            cap.release()
            cv2.destroyAllWindows()
            return
    cap.release()
    cv2.destroyAllWindows()


def loop(src, roi):
    while True:
        # s = lirc.nextcode(1)
        s = pylirc.nextcode(1)

        while (s):
            for (code) in s:
                print(current_time + '-'+'Command: ', code["config"])
                # take_camera(code["config"])
                IR(code["config"], src, roi)
            if (not blocking):
                s = pylirc.nextcode(1)
                # s = lirc.nextcode(1)
            else:
                s = []


def destroy():
    GPIO.cleanup()
    # servo.stop()
    pwm.softwareReset()  # 重置PWM扩展板
    pylirc.exit()


def main(flag):
    log()
    global L_Motor
    global R_Motor
    GPIO.cleanup()
    L_Motor = 0
    R_Motor = 0
    setup()
    # print("hello")
    L_Motor = GPIO.PWM(PWMA, 100)
    L_Motor.start(0)
    R_Motor = GPIO.PWM(PWMB, 100)
    R_Motor.start(0)
    #keysacn()
    GPIO.output(LED, True)
    pylirc.init("pylirc", "/home/pi/Desktop/LCDMenu/conf", blocking)
    try:
        take_camera(flag)
    except KeyboardInterrupt:
        destroy()



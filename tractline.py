import time
import sys
import logging
import os
import RPi.GPIO as GPIO

T_SensorRight = 26
T_SensorLeft = 13

PWMA = 18
AIN1 = 22
AIN2 = 27

PWMB = 23
BIN1 = 25
BIN2 = 24

BtnPin = 19
Gpin = 5
Rpin = 6
CANCEL = 14
LED = 11
L_Motor = 0
R_Motor = 0



def log():
    log_path = '/home/pi/Desktop/LCDMenu/Logs/'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                        datefmt='%a %d %b %Y %H:%M:%S',
                        filename=log_path + 'IR line following: ' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.log',
                        filemode='w')



def t_up(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, True)  # AIN2
    GPIO.output(AIN1, False)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, True)  # BIN2
    GPIO.output(BIN1, False)  # BIN1
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
    GPIO.output(AIN2, False)  # AIN2
    GPIO.output(AIN1, True)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, True)  # BIN1
    time.sleep(t_time)


def t_left(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, False)  # AIN2
    GPIO.output(AIN1, True)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, True)  # BIN2
    GPIO.output(BIN1, False)  # BIN1
    time.sleep(t_time)


def t_right(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, True)  # AIN2
    GPIO.output(AIN1, False)  # AIN1

    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, True)  # BIN1
    time.sleep(t_time)


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
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
    GPIO.setup(Gpin, GPIO.OUT)  # Set Green Led Pin mode to output
    GPIO.setup(Rpin, GPIO.OUT)  # Set Red Led Pin mode to output
    GPIO.setup(BtnPin, GPIO.IN,
               pull_up_down=GPIO.PUD_UP)  # Set BtnPin's mode is input, and pull up to high level(3.3V)
    GPIO.setup(T_SensorRight, GPIO.IN)
    GPIO.setup(T_SensorLeft, GPIO.IN)

    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(PWMA, GPIO.OUT)

    GPIO.setup(BIN1, GPIO.OUT)
    GPIO.setup(BIN2, GPIO.OUT)
    GPIO.setup(PWMB, GPIO.OUT)
    GPIO.setup(CANCEL, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(LED, GPIO.OUT)


def main(flag):
    global L_Motor
    global R_Motor
    setup()
    log()
#     keysacn()
    L_Motor = 0
    R_Motor = 0
    L_Motor = GPIO.PWM(PWMA, 100)
    L_Motor.start(0)
    R_Motor = GPIO.PWM(PWMB, 100)
    R_Motor.start(0)
    try:
        while True:

            if GPIO.input(CANCEL) == 0:
                L_Motor = 0
                R_Motor = 0
                GPIO.cleanup()
                return
            SR = GPIO.input(T_SensorRight)
            SL = GPIO.input(T_SensorLeft)

            if SL == False and SR == False:
                # print("t_up")
                logging.info("forward")
                if flag == 'extensive':
                    logging.info("no deviation")
                    logging.info("forward")
                t_up(30, 0.01)

            elif SL == True and SR == False:
                # print("Right")
                logging.info("turn right")
                if flag == 'extensive':
                    logging.info("right offset")
                    logging.info("turn right")
                t_right(33, 0.1)

            elif SL == False and SR == True:
                # print("Left")
                logging.info("turn left")
                if flag == 'extensive':
                    logging.info("right offset")
                    logging.info("turn right")
                t_left(33, 0.1)
                
            else:
                logging.info("stop")
                if flag == 'extensive':
                    logging.info("no line")
                    logging.info("stop")
                t_stop(0)
            
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        GPIO.cleanup()

def judge():
    global stop
    setup()
    stop = 1
    try:
        SR = GPIO.input(T_SensorRight)
        SL = GPIO.input(T_SensorLeft)
        if SL == True and SR == False:
            stop == 0
        return stop
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        GPIO.cleanup()

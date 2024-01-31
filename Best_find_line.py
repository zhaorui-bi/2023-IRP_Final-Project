import numpy as np
import cv2
import time
import logging
import os
import math
import tractline
import RPi.GPIO as GPIO

PWMA = 18
AIN1 = 27
AIN2 = 22

PWMB = 23
BIN1 = 24
BIN2 = 25
CANCEL = 14
LED = 11
L_Motor = 0
R_Motor = 0

T_SensorRight = 26
T_SensorLeft = 13

lower_color_dir = {'blue': [100, 50, 50], 'green': [75, 50, 50],
                   'red': [0, 90, 90], 'black': [0, 0, 0],
                   'yellow': [30, 50, 50]}
upper_color_dir = {'blue': [130, 255, 255], 'green': [95, 255, 255],
                   'red': [10, 255, 255], 'black': [180, 255, 30],
                   'yellow': [60, 255, 255]}

para_speed = 35
turning_speed = 23
left_count = 0
right_count = 0
threahold = 5

left = []
right = []
forward = []


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def log():
    log_path = '/home/pi/Desktop/LCDMenu/Logs/'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                        datefmt='%a %d %b %Y %H:%M:%S',
                        filename=log_path + 'Free Travel: ' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.log',
                        filemode='w')
  

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(PWMA, GPIO.OUT)
    GPIO.setup(AIN2,GPIO.OUT)
    GPIO.setup(AIN1,GPIO.OUT)
    GPIO.setup(PWMB, GPIO.OUT)
    GPIO.setup(BIN1,GPIO.OUT)
    GPIO.setup(BIN2,GPIO.OUT)
    GPIO.setup(CANCEL, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(LED, GPIO.OUT)


def forward(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2,False)#AIN2
    GPIO.output(AIN1,True) #AIN1
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, True)  # BIN1


def stop():
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(AIN2, False)  # AIN2
    GPIO.output(AIN1, False)  # AIN1
    R_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, False)  # BIN1


def backward(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, True)  # AIN2
    GPIO.output(AIN1, False)  # AIN1
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, True)  # BIN2
    GPIO.output(BIN1, False)  # BIN1


def turn_left(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, True)  # AIN2
    GPIO.output(AIN1, False)  # AIN1
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, False)  # BIN2
    GPIO.output(BIN1, True)  # BIN1

def turn_right(speed):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN2, False)  # AIN2
    GPIO.output(AIN1, True)  # AIN1
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN2, True)  # BIN2
    GPIO.output(BIN1, False)  # BIN1


def Intersection_calculations(A, B, C, D): 
    a1 = B.y - A.y
    b1 = A.x - B.x
    c1 = a1*(A.x) + b1*(A.y)
    a2 = D.y - C.y
    b2 = C.x - D.x
    c2 = a2*(C.x) + b2*(C.y)
    judgment = a1*b2 - a2*b1
    if (judgment == 0):
        return Point(10**9, 10**9)
    else:
        global X,Y
        x = (b2*c1 - b1*c2)/judgment
        y = (a1*c2 - a2*c1)/judgment
        return Point(x, y)


def are_lists_equal(list1, list2):
    if len(list1) != len(list2):
        return False
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            return False
    return True


def Horizontal_angle(x1, y1, x2, y2)->float:
    # Calculate the horizontal angle
    slope = (y2 - y1) / (x2 - x1)
    Horizontal_radians = math.atan(slope)
    Horizontal_degrees = math.degrees(Horizontal_radians)
    return Horizontal_degrees


def vertical_angle(x1, y1, x2, y2)->float:
    # Calculate the vertical angle
    slope = (y2 - y1) / (x2 - x1)
    vertical_radians = math.atan(1 / slope)
    vertical_degrees = math.degrees(vertical_radians)
    return vertical_degrees


def judge_path_type(first_frame, mask):
    Blue_frame = cv2.bitwise_and(first_frame, first_frame, mask=mask)
    final_frame = cv2.cvtColor(Blue_frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(final_frame, 60, 110)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40, minLineLength=30, maxLineGap=300)
    if lines is not None:
        parallel = None
        vertical = None
        judge = [False, False, False]
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Calculate the slope
            if x1 == x2:
                k = np.inf
            else:
                k = float(abs(y2-y1)/abs(x2-x1))
            if parallel is not None and vertical is not None:
                break
            elif vertical is None and k > 1.6:
                vertical = line[0]
                cv2.putText(first_frame, f'Vertical Angle:{vertical_angle(vertical[0],vertical[1],vertical[2],vertical[3])}',
                            (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0,0,255), 2)
            elif parallel is None and 0 < k < 1.6:
                parallel = line[0]
                cv2.putText(first_frame, f'Horizontal Angle:{Horizontal_angle(parallel[0],parallel[1],parallel[2],parallel[3])}',
                            (200, 70), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0,255,0), 2)

        if vertical is not None:
            x1, y1, x2, y2 = vertical
            cv2.line(first_frame, (x1, y1), (x2, y2), (0,255,0), 2)
        if parallel is not None:
            x1, y1, x2, y2 = parallel
            cv2.line(first_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        if parallel is not None and vertical is not None:
            A = Point(parallel[0], parallel[1])
            B = Point(parallel[2], parallel[3])
            C = Point(vertical[0], vertical[1])
            D = Point(vertical[2], vertical[3])
            intersection = Intersection_calculations(A, B, C, D)
            X = intersection.x
            Y = intersection.y
            distance = math.sqrt((X-480) ** 2 + (Y-360) ** 2)
            cv2.putText(first_frame,f'Distance:{distance}',
                        (200, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 0, 0), 2)
            if parallel[0] < parallel[2]:
                left = parallel[:2]
                right = parallel[2:]
            else:
                left = parallel[2:]
                right = parallel[:2]
            if vertical[1] < vertical[3]:
                forward = vertical[:2]
            else:
                forward = vertical[2:]

            if distance1 > 100:
                judge[0] = True
            if distance2 > 100:
                judge[1] = True
            if are_lists_equal(judge, list3):       
                return 'right'
            elif are_lists_equal(judge, list4):      
                return 'left'
        elif parallel is None and vertical is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if math.sqrt((x1 - x2) ** 2 + (y1 - x2) ** 2) <= 120:
                    
                    return 'short'
                    cv2.putText(first_frame, f'Short Distance:{math.sqrt((x1 - x2) ** 2 + (y1 - x2) ** 2)}',
                                (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 0, 0), 2)
                else:
    
                    return 'long'


def camera_line(color,flag):
    global left_count, right_count, L_Motor, R_Motor
    para_speed = 35
    para_color = color
        
    GPIO.cleanup()
    L_Motor = 0
    R_Motor = 0
    setup()
    log()
    L_Motor = GPIO.PWM(PWMA, 100)
    L_Motor.start(0)
    R_Motor = GPIO.PWM(PWMB, 100)
    R_Motor.start(0)  
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    start_time = time.time()
    frame_count = 0
    GPIO.output(LED, True)
    while True:
        if GPIO.input(CANCEL) == 0:
            L_Motor = 0
            R_Motor = 0
            GPIO.cleanup()
            return
        
        ret, frame = cap.read()
        if GPIO.input(CANCEL) == 0:
            GPIO.cleanup()
            L_Motor = 0
            R_Motor = 0
            return

        if frame is None:
            continue
        size_x = 400
        size_y = 400
        x = (640 - size_x) // 2
        y = (480 - size_y) // 2
        crop_frame = frame[y:y + size_y, x:x + size_x]

        hsv = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2HSV)
        lower_color = np.array(lower_color_dir[para_color])
        upper_color = np.array(upper_color_dir[para_color])
        mask = cv2.inRange(hsv, lower_color, upper_color)

        blur = cv2.GaussianBlur(mask, (5, 5), 0)
        if color =='blue':
            result = judge_path_type(crop_frame, mask)
            print(result,'123')      
        else:
            result = 'long'
        
        _, contours, hierarchy = cv2.findContours(
            blur.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            if len(c) > 0:
                M = cv2.moments(c)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv2.line(crop_frame, (cx, 0), (cx, 720),
                         (255, 0, 0), 1)
                cv2.line(crop_frame, (0, cy),
                         (1280, cy), (255, 0, 0), 1)  
            if result == 'long' and para_color=='black':      
                if cx < 250 and cx > 155:
                     forward(20)
                     logging.info("move forward")
                elif cx > 250 and cx < 410:
                     turn_right(18)
                     logging.info("turn weak right")
                elif cx < 155 and cx > 0:
                     turn_left(18)
                     logging.info("turn weak left")
                if flag == 'extensive':
                     logging.info("detect long")
            if result == 'long' and para_color=='blue':
                if flag == 'extensive':
                     logging.info("detect long")
                if cx < 280 and cx > 180:
                    forward(20)
                    logging.info("move forward")
                elif cx > 280 and cx < 380:
                    logging.info("turn weak right")
                    turn_right(16)
                elif cx < 180 and cx > 0:
                    turn_left(16)
                    logging.info("turn weak left")
            if result == 'long' and (para_color=='green'or para_color=='red'):
                if flag == 'extensive':
                    logging.info("detect long")
                if cx < 270 and cx > 190:
                    forward(25)
                    logging.info("move forward")
                elif cx > 270 and cx < 390:
                    logging.info("turn weak right")
                    turn_right(18)
                elif cx < 190 and cx > 0:
                    turn_left(18)
                    logging.info("turn weak left")
            
            if result == 'long' and para_color=='yellow':
                 if cx < 270 and cx > 190:
                     forward(25)
                 elif cx > 270 and cx < 390:
                     turn_right(16)
                 elif cx < 190 and cx > 0:
                     turn_left(18)

            elif result == None:
                stop()
                time.sleep(5)
                print("stop")
            elif result == 'left':
                left_count += 1
                if flag == 'extensive':
                    logging.info("detect left corner")
                    logging.info("turn left")
                if left_count >= threahold:
                    forward(25)
                    time.sleep(1.8)
                    while True:
                        turn_left(turning_speed)
                        ret, frame = cap.read()
                        size_x = 400
                        size_y = 400
                        x = (640 - size_x) // 2
                        y = (480 - size_y) // 2
                        crop_frame = frame[y:y + size_y, x:x + size_x]                 
                        hsv = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2HSV)
                        lower_blue = np.array([100, 50, 50])
                        upper_blue = np.array([130, 255, 255])
                        mask = cv2.inRange(hsv, lower_blue, upper_blue)
                        blur = cv2.GaussianBlur(mask, (5, 5), 0)
                        result = judge_path_type(crop_frame, mask)
                        if GPIO.input(CANCEL) == 0:
                            GPIO.cleanup()
                            L_Motor = 0
                            R_Motor = 0
                            return
                        if result == 'long':
                            break
            elif result == 'right':
                if flag == 'extensive':
                    logging.info("detect right corner")
                    logging.info("turn right")
                right_count += 1
                if right_count >= threahold:
                    forward(25)
                    time.sleep(1.8)
                    while True:
                        turn_right(turning_speed)
                        ret, frame = cap.read()
                        size_x = 400
                        size_y = 400
                        x = (640 - size_x) // 2
                        y = (480 - size_y) // 2
                        crop_frame = frame[y:y + size_y, x:x + size_x]
                        hsv = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2HSV)
                        lower_blue = np.array([100, 50, 50])
                        upper_blue = np.array([130, 255, 255])
                        mask = cv2.inRange(hsv, lower_blue, upper_blue)
                        blur = cv2.GaussianBlur(mask, (5, 5), 0)
                        if GPIO.input(CANCEL) == 0:
                            GPIO.cleanup()
                            L_Motor = 0
                            R_Motor = 0
                            return
                        result = judge_path_type(crop_frame, mask)
                        if result == 'long':
                            break


def main(para_color, flag):
    try:
        log()
        camera_line(para_color,flag)
    except KeyboardInterrupt:
        pass

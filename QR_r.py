import cv2
import numpy as np
import sys
import os
import time
import pyzbar.pyzbar as pyzbar


lastInfo = "info"
number_photo =1
cv2.namedWindow("Photo_Detect")


class Logger(object):
    def __init__(self, file_name="Default.log", stream=sys.stdout):
        self.terminal = stream
        self.log = open(file_name, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


def log():
    log_path = '/home/pi/Desktop/rb/QR/Logs/'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file_name = log_path + 'log-' + 'QR code detection ' + time.strftime("%Y%m%d-%H%M%S", time.localtime()) + '.log'
    sys.stdout = Logger(log_file_name)
    sys.stderr = Logger(log_file_name)

def opencvQR(src):

    global number_photo
    global lastInfo
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
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)

    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        if (barcodeData != "") & (barcodeData != lastInfo):
            result = np.copy(roi)
            print("qrcode : %s" % barcodeData)
            cv2.putText(result, "qrcode:" + str(barcodeData), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2);
            cv2.putText(result, str(number_photo) + ' QR code', (800, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2);
            stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(number_photo)
            new_folder = '/home/pi/Desktop/rb/QR/Photos/'
            os.makedirs(new_folder, exist_ok=True)
            save_path = os.path.join(new_folder, time.strftime("%Y%m%d-%H%M%S", time.localtime()) + " " + str(
                number_photo) + ' QR code.jpg')
            cv2.imwrite(save_path, src)
            # cv2.imwrite(str(number_photo) +' QR code.jpg', result)
            number_photo = number_photo + 1
            lastInfo = barcodeData


def video_demo():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow('Photo_Detect', frame)
        opencvQR(frame)

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def take_screenshot():
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
        roi_size = 200
        roi_left = center_x - int(roi_size / 2)
        roi_top = center_y - int(roi_size / 2)
        roi_right = center_x + int(roi_size / 2)
        roi_bottom = center_y + int(roi_size / 2)
        roi = src[roi_top:roi_bottom, roi_left:roi_right]
        cv2.imshow('center', roi)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(gray)

        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            if barcodeData != "":
                result = np.copy(roi)
                print("qrcode : %s" % barcodeData)
                cv2.putText(result, "qrcode:" + str(barcodeData), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2);
                cv2.putText(result, str(number_photo) + ' QR code', (800, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2);
                stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                print(number_photo)
                new_folder = '/home/pi/Desktop/rb/QR/Photos/'
                os.makedirs(new_folder, exist_ok=True)
                save_path = os.path.join(new_folder, time.strftime("%Y%m%d-%H%M%S", time.localtime()) + " " + str(
                    number_photo) + ' QR code.jpg')
                cv2.imwrite(save_path, src)
                # cv2.imwrite(str(number_photo) +' QR code.jpg', result)
                number_photo = number_photo + 1


        if number_photo == 2:
            break

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

def screenshot(timevalue):
    global number_photo
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    run_time = timevalue
    while True:
        ret, src = cap.read()

        if not ret:
            break

        cv2.imshow('Photo_Detect', src)

        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(gray)

        for barcode in barcodes:
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            if barcodeData != "":
                result = np.copy(src)
                print("qrcode : %s" % barcodeData)
                cv2.putText(result, "qrcode:" + str(barcodeData), (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2);
                cv2.putText(result, str(number_photo) + ' QR code', (800, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2);
                stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                #print(number_photo)
                new_folder = '/home/pi/Desktop/rb/QR/Photos/'
                os.makedirs(new_folder, exist_ok=True)
                save_path = os.path.join(new_folder, time.strftime("%Y%m%d-%H%M%S", time.localtime()) + " " + str(
                    number_photo) + ' QR code.jpg')
                cv2.imwrite(save_path, src)
                # cv2.imwrite(str(number_photo) +' QR code.jpg', result)
                number_photo = number_photo + 1


        if number_photo == 2:
            number_photo = 1
            break

        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

        if time.time() - start_time > run_time:
            print("can not detect qr code")
            break

    cap.release()
    cv2.destroyAllWindows()


screenshot(2)
screenshot(2)

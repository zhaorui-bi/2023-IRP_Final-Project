#!/usr/bin/python

import RPi.GPIO as GPIO
import time



# GPIO to LCD mapping
LCD_RS = 7  # Pi pin 26
LCD_E = 8  # Pi pin 24
LCD_D4 = 4  # Pi  pin 22
LCD_D5 = 12  # Pi pin 18
LCD_D6 = 16  # Pi pin 16
LCD_D7 = 17  # Pi pin 12
# LED = 11
UP = 9
DOWN = 15
CONFIRM = 10
CANCEL = 14

# Device constants
LCD_CHR = True  # Character mode
LCD_CMD = False  # Command mode
LCD_CHARS = 16  # Characters per line (16 max)
LCD_LINE_1 = 0x80  # LCD memory location for 1st line
LCD_LINE_2 = 0xC0  # LCD memory location 2nd line
cur_speed = 100
cur_light = 'auto'
cur_log = 'disabled'
cur_distance = 20
cur_colour = 'blue'
set_status = 0


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # Set GPIO's to output mode
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)
#     GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(UP, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(DOWN, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(CONFIRM, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(CANCEL, GPIO.IN, GPIO.PUD_UP)
    # Initialize display
    lcd_init()

    # Loop - send text and sleep 3 seconds between texts


# Initialize and clear display
def lcd_init():
    lcd_write(0x33, LCD_CMD)  # Initialize
    lcd_write(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_write(0x06, LCD_CMD)  # Cursor move direction
    lcd_write(0x0C, LCD_CMD)  # Turn cursor off
    lcd_write(0x28, LCD_CMD)  # 2 line display
    lcd_write(0x01, LCD_CMD)  # Clear display
    time.sleep(0.0005)  # Delay to allow commands to process


def lcd_write(bits, mode):
    GPIO.output(LCD_RS, mode)  # RS
    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)

    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)

    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()


def lcd_toggle_enable():
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)


def lcd_text(message, line):
    # Send text to display
    message = message.ljust(LCD_CHARS, ' ')
    lcd_write(line, LCD_CMD)
    for i in range(LCD_CHARS):
        lcd_write(ord(message[i]), LCD_CHR)


class menu():
    def __init__(self):
        main()
#         GPIO.output(LED, True)

    def lv1(self):
        lcd_text(">IR", LCD_LINE_1)
        print(">IR")
        lcd_text(" Camera", LCD_LINE_2)
        print(" Camera")
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.lv5()
                return
            elif GPIO.input(DOWN) == 0:
                self.lv2()
                return
            elif GPIO.input(CONFIRM) == 0:
                self.function1()
                return

    def lv2(self):
        lcd_text(" IR", LCD_LINE_1)
        print(" IR")
        lcd_text(">Camera", LCD_LINE_2)
        print(">Camera")
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                return
            elif GPIO.input(DOWN) == 0:
                self.lv3()
                return
            elif GPIO.input(CONFIRM) == 0:
                self.function2()
                return

    def lv3(self):
        lcd_text(">free_travel", LCD_LINE_1)
        print(">free_travel")
        lcd_text(" remote_control", LCD_LINE_2)
        print(" remote_control")
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.lv2()
                return
            elif GPIO.input(DOWN) == 0:
                self.lv4()
                return
            elif GPIO.input(CONFIRM) == 0:
                self.function3()
                return

    def lv4(self):
        lcd_text(" free_travel", LCD_LINE_1)
        print(" free_travel")
        lcd_text(">remote_control", LCD_LINE_2)
        print(">remote_control")
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.lv3()
                return
            elif GPIO.input(DOWN) == 0:
                self.lv5()
                return
            elif GPIO.input(CONFIRM) == 0:
                self.function4()
                return

    def lv5(self):
        lcd_text(">settings", LCD_LINE_1)
        print(">settings")
        lcd_text("", LCD_LINE_2)
        print("")
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.lv4()
                return
            elif GPIO.input(DOWN) == 0:
                return
            elif GPIO.input(CONFIRM) == 0:
                while True:
                    set = setting()
                    set.setting_lv1()
                    if GPIO.input(CANCEL) == 0:
                        return

    def function1(self):
        self.IR(cur_speed, cur_light)
        return

    def function2(self):
        self.Camera(cur_speed, cur_speed, cur_log, cur_colour)
        return

    def function3(self):
        self.free_trav(cur_speed, cur_light, cur_distance)
        return

    def function4(self):
        self.remote_ctrl(cur_speed, cur_light)
        return

    def IR(self, speed, light):
        lcd_text(f"s:{speed} l:{light}", LCD_LINE_1)
        print(f"s:{speed} l:{light}")
        lcd_text('', LCD_LINE_2)
        print("")
        GPIO.cleanup()
        import tractline
        set = setting()
        tractline.main(cur_log)
#         L_Motor = 0
#         R_Motor = 0
        main()

    def Camera(self, speed, light, log, colour):
        lcd_text(f"s:{speed} l:{light}", LCD_LINE_1)
        print(f"s:{speed} l:{light}")
        lcd_text(f"lg:{log} c:{colour}", LCD_LINE_2)
        print(f"lg:{log} c:{colour}")
        import Best_find_line
        set = setting()
        Best_find_line.main(cur_colour, cur_log)
        main()


    def free_trav(self, speed, light, distance):
        lcd_text(f"s:{speed} l:{light}", LCD_LINE_1)
        print(f"s:{speed} l:{light}")
        lcd_text(f"d:{distance}", LCD_LINE_2)
        print(f"d:{distance}")
        # 添加函数here
        GPIO.cleanup()
        import Ultrasonic_obstacle_avoidance
        set = setting()
        Ultrasonic_obstacle_avoidance.main(cur_log)
        main()


    def remote_ctrl(self, speed, light):
        lcd_text(f"s:{speed} l:{light}", LCD_LINE_1)
        print(f"s:{speed} l:{light}")
        lcd_text('', LCD_LINE_2)
        print("")
        GPIO.cleanup()
        import remote_control_final_logging
        set = setting()
        remote_control_final_logging.main(cur_log)
        main()





class setting():

    def __init__(self):
        self.para_log = ['disabled', 'minimal', 'extensive']
        self.para_distance = [20, 40, 80, 100]
        self.para_speed = [25, 50, 75, 100]
        self.para_light = ['on', 'off', 'auto']
        self.para_colour = ['red', 'green', 'blue', 'black', 'yellow']

    def setting_lv1(self):
        global set_status
        lcd_text(">{}: {}".format('SPEED', cur_speed), LCD_LINE_1)
        print(">{}: {}".format('SPEED', cur_speed))
        lcd_text(" {}: {}".format('LIGHT', cur_light), LCD_LINE_2)
        print(" {}: {}".format('LIGHT', cur_light))
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.setting_lv5()
                return
            elif GPIO.input(DOWN) == 0:
                self.setting_lv2()
                return
            elif GPIO.input(CONFIRM) == 0:
                set_status = 1
                self.para_lv1(self.para_speed)
                return
            elif GPIO.input(CANCEL) == 0:
                return

    def setting_lv2(self):
        global set_status
        lcd_text(" {}: {}".format('SPEED', cur_speed), LCD_LINE_1)
        print(" {}: {}".format('SPEED', cur_speed))
        lcd_text(">{}: {}".format('LIGHT', cur_light), LCD_LINE_2)
        print(">{}: {}".format('LIGHT', cur_light))
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                return
            elif GPIO.input(DOWN) == 0:
                self.setting_lv3()
                return
            elif GPIO.input(CONFIRM) == 0:
                set_status = 2
                self.para_lv1(self.para_light)
                return
            elif GPIO.input(CANCEL) == 0:
                return

    def setting_lv3(self):
        global set_status
        lcd_text(">{}: {}".format('LOG', cur_log), LCD_LINE_1)
        print(">{}: {}".format('LOG', cur_log))
        lcd_text(" {}: {}".format('DISTANCE', cur_distance), LCD_LINE_2)
        print(" {}: {}".format('DISTANCE', cur_distance))
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.setting_lv2()
                return
            elif GPIO.input(DOWN) == 0:
                self.setting_lv4()
                return
            elif GPIO.input(CONFIRM) == 0:
                set_status = 3
                self.para_lv1(self.para_log)
                return
            elif GPIO.input(CANCEL) == 0:
                return

    def setting_lv4(self):
        global set_status
        lcd_text(" {}: {}".format('LOG', cur_log), LCD_LINE_1)
        print(" {}: {}".format('LOG', cur_log))
        lcd_text(">{}: {}".format('DISTANCE', cur_distance), LCD_LINE_2)
        print(">{}: {}".format('DISTANCE', cur_distance))
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.setting_lv3()
                return
            elif GPIO.input(DOWN) == 0:
                self.setting_lv5()
                return
            elif GPIO.input(CONFIRM) == 0:
                set_status = 4
                self.para_lv1(self.para_distance)
                return
            elif GPIO.input(CANCEL) == 0:
                return

    def setting_lv5(self):
        global set_status
        lcd_text(f">color: {cur_colour}", LCD_LINE_1)
        print(f">color: {cur_colour}")
        lcd_text("", LCD_LINE_2)
        print("")
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.setting_lv4()
                return
            elif GPIO.input(DOWN) == 0:
                return
            elif GPIO.input(CONFIRM) == 0:
                set_status = 5
                self.para_lv1(self.para_colour)
                return
            elif GPIO.input(CANCEL) == 0:
                return

    def change(self, para):
        global set_status
        global cur_speed
        global cur_light
        global cur_log
        global cur_distance
        global cur_colour
        if set_status == 1:
            cur_speed = para
            return
        elif set_status == 2:
            cur_light = para
            return
        elif set_status == 3:
            cur_log = para
            return
        elif set_status == 4:
            cur_distance = para
            return
        elif set_status == 5:
            cur_colour = para
            return

    def para_lv1(self, para):
        if len(para) == 4:
            lcd_text(f">{para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}   {para[3]}", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv4(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv2(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[0])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return
        elif len(para) == 3:
            lcd_text(f">{para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}     ", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv3(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv2(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[0])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return
        elif len(para) == 5:
            lcd_text(f">{para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}   {para[3]}", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv5(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv2(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[0])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return

    def para_lv2(self, para):
        if len(para) == 4:
            lcd_text(f" {para[0]}  >{para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}   {para[3]}", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv1(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv3(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[1])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return
        elif len(para) == 3:
            lcd_text(f" {para[0]}  >{para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}     ", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv1(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv3(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[1])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return
        elif len(para) == 5:
            lcd_text(f" {para[0]}  >{para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}   {para[3]}", LCD_LINE_2) 
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv1(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv3(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[1])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return

    def para_lv3(self, para):
        if len(para) == 4:
            lcd_text(f" {para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f">{para[2]}   {para[3]}", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv2(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv4(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[2])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return
        elif len(para) == 3:
            lcd_text(f" {para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f">{para[2]}     ", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv2(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv1(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[2])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return
        elif len(para) == 5:
            lcd_text(f" {para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f">{para[2]}   {para[3]}", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv2(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv4(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[2])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return

    def para_lv4(self, para):
        if len(para) == 4:
            lcd_text(f" {para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}  >{para[3]}", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv3(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv1(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[3])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return
        elif len(para) == 5:
            lcd_text(f" {para[0]}   {para[1]}", LCD_LINE_1)
            lcd_text(f" {para[2]}  >{para[3]}", LCD_LINE_2)
            time.sleep(0.2)
            while True:
                if GPIO.input(UP) == 0:
                    self.para_lv3(para)
                    return
                elif GPIO.input(DOWN) == 0:
                    self.para_lv5(para)
                    return
                elif GPIO.input(CONFIRM) == 0:
                    self.change(para[3])
                    return
                elif GPIO.input(CANCEL) == 0:
                    time.sleep(0.2)
                    return

    def para_lv5(self, para):
        lcd_text(f">{para[4]}   ", LCD_LINE_1)
        lcd_text(" ", LCD_LINE_2)
        time.sleep(0.2)
        while True:
            if GPIO.input(UP) == 0:
                self.para_lv4(para)
                return
            elif GPIO.input(DOWN) == 0:
                self.para_lv1(para)
                return
            elif GPIO.input(CONFIRM) == 0:
                self.change(para[4])
                return
            elif GPIO.input(CANCEL) == 0:
                time.sleep(0.2)
                return


if __name__ == '__main__':
    try:
        while True:
            x = menu()
            x.lv1()
    finally:
        
        
        
        
        
        
        
        
        
        
        lcd_write(0x01, LCD_CMD)
        GPIO.cleanup()

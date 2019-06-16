from RPi import GPIO
import time


class LCD:

    def __init__(self, pinarray, clock, rs):
        self.pins = pinarray
        self.clock = clock
        self.rs = rs

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinarray, GPIO.OUT)
        GPIO.setup(clock, GPIO.OUT)
        GPIO.setup(rs, GPIO.OUT)

        GPIO.output(clock, 1)

    def init_lcd(self):
        self.write_byte(0x38, instruction=True)

    def reset(self):
        self.write_byte(0b1, instruction=True)

    def display_on(self):
        self.write_byte(0b1100, instruction=True)

    @staticmethod
    def write_one_bit(pin, bit):
        GPIO.output(pin, bit)

    def write_byte(self, byte, instruction=False):
        if instruction:
            GPIO.output(self.rs, 0)
        else:
            GPIO.output(self.rs, 1)

        GPIO.output(self.clock, 1)
        mask = 1
        for i in reversed(range(8)):
            bit = byte & (mask << i)
            self.write_one_bit(self.pins[i], bit)

        GPIO.output(self.clock, 0)
        time.sleep(0.01)

    def send_char(self, c):
        ascii_code = ord(c)
        # print("Sending char: '{0}': {1} = 0b{1:0=8b}".format(c, ascii_code))
        self.write_byte(ascii_code)

    def send_string(self, s, secondrow):
        if secondrow:
            self.write_byte((0b1 << 7) | 0x40, instruction=True)
        else:
            self.write_byte((0b1 << 7) | 0x0, instruction=True)

        for i in s:
            self.send_char(i)


# pins = [16, 12, 25, 24, 23, 26, 19, 13]
# clock = 20
# rs = 21
#
#
# def setup():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(pins, GPIO.OUT)
#     GPIO.setup(clock, GPIO.OUT)
#     GPIO.setup(rs, GPIO.OUT)
#
#     GPIO.output(clock, 1)
#
#
# try:
#     lcd = LCD(pins, clock, rs)
#     lcd.init_lcd()
#     lcd.display_on()
#     lcd.reset()
#     lcd.send_string("YEETUS", False)
#     lcd.send_string("DAT FEETUS", True)
#     # time.sleep(2)
#     # time.sleep(2)
#     # send_string("FUNNYY")
#     while True:
#         pass
#         # send_string("Be or not to be")
#         # write_byte(0b11000000, True)
#
#         # time.sleep(1)
# except KeyboardInterrupt:
#     print("Ok, Bye!")
# except Exception as ex:
#     print("Error: {0}".format(ex))
# finally:
#     GPIO.cleanup()

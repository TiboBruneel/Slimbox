import time
import serial


class SerialClass:

    # INIT / START
    def __init__(self, par_port, par_baudrate=9600, par_parity=serial.PARITY_NONE, par_stopbits=serial.STOPBITS_ONE,
                 par_bytesize=serial.EIGHTBITS, par_timeout=1):
        self.__port = par_port
        self.__baudrate = par_baudrate
        self.__parity = par_parity
        self.__stopbits = par_stopbits
        self.__bytesize = par_bytesize
        self.__timeout = par_timeout

        self.arduino = serial.Serial(str(self.__port), baudrate=self.__baudrate, parity=self.__parity,
                                     stopbits=self.__stopbits, bytesize=self.__bytesize, timeout=self.__timeout)

    # Functies

    def write(self, par_input):
        self.arduino.write(bytes(par_input, "utf-8"))
        time.sleep(1)

    def lees(self):
        reaction = self.arduino.readline()
        print(reaction)

    def sluit_poort(self):
        self.arduino.close()

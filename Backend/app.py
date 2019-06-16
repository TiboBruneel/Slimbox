from flask import Flask, jsonify, request, url_for, json
from flask_cors import CORS
from threading import Thread
from database import DP1Database
import time
import datetime
from flask_socketio import SocketIO
from classes import MCP, LCD, Serialclass
from subprocess import check_output
import subprocess
import smbus
from RPi import GPIO
from threading import Lock

serial = Serialclass.SerialClass('/dev/ttyS0')
serial.write("Red")
colorReload = {"color": "Red"}


class TempCheck(Thread):  # Parent van Thread
    def __init__(self):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond

        self.tempValue = 0

        self.start()  # Start de aparte thread

    def lees_temperatuur(self):
        temperature_filename = '/sys/bus/w1/devices/w1_bus_master1/28-021624e708ee/w1_slave'
        file = open(temperature_filename)
        temperature_result = float(file.readlines()[1].split("t=")[-1]) / 1000
        return round(temperature_result, 1)

    def run(self):  # Dit wordt gerunt door self.start().
        #  de run functie niet zelf starten. je moet de effectieve thread starten
        time.sleep(0.5)
        print("Ready")
        while True:
            current_time = datetime.datetime.now()
            datum = str(current_time)[0:16]
            temp = self.lees_temperatuur()
            self.tempValue = temp
            row_inserted = conn.set_data(
                "insert into SensorenHistoriek(EventDatum, SensorID, Waarde) values (%s, %s, %s)",
                [datum, 1, temp])
            if int(row_inserted) > 0:
                print("Temp stored in database")
            time.sleep(600)


class VolumeCheck(Thread):  # Parent van Thread
    def __init__(self):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond

        self.mcp = MCP.Mcp()
        self.mcp.open()

        self.volume_last = 0
        self.volumeValue = 0

        self.start()  # Start de aparte thread

    def lees_volume(self):
        potentio_result = round(self.mcp.read_channel(1) / 1023 * 100)
        return potentio_result

    def run(self):  # Dit wordt gerunt door self.start().
        #  de run functie niet zelf starten. je moet de effectieve thread starten
        time.sleep(0.5)
        print("Ready")
        while True:
            current_time = datetime.datetime.now()
            datum = str(current_time)[0:16]
            volume = self.lees_volume()

            if volume != self.volume_last and volume != (self.volume_last - 1) and volume != (self.volume_last + 1) \
                    and volume != (self.volume_last - 2) and volume != (self.volume_last + 2):
                print(volume)
                self.volume_last = volume
                self.volumeValue = volume
                socketio.emit("volume", volume)
                print("Volume Value: {0}".format(self.volumeValue))
                row_inserted = conn.set_data(
                    "insert into SensorenHistoriek(EventDatum, SensorID, Waarde) values (%s, %s, %s)",
                    [datum, 2, volume])
                if int(row_inserted) > 0:
                    print("Temp stored in database")
                command = "amixer cset numid=1 -- {0}%".format(volume)
                subprocess.call(command, shell=True)
                time.sleep(.5)


class StatusCheck(Thread):  # Parent van Thread
    def __init__(self, volume):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond
        self.start()  # Start de aparte thread
        self.volume = volume
        self.bus = smbus.SMBus(1)
        self.bus.write_byte_data(0x19, 0x20, 0x27)
        self.bus.write_byte_data(0x19, 0x23, 0x00)

        self.status = 1
        self.status_change = 0
        self.status_database = "Playing"
        self.xAccl = 0

    def lees_potentio(self):
        data0 = self.bus.read_byte_data(0x19, 0x28)
        data1 = self.bus.read_byte_data(0x19, 0x29)

        xAccl = data1 * 256 + data0
        if xAccl > 32767:
            xAccl -= 65536

        xAccl = round(xAccl / 32767 * 10)
        return xAccl

    def run(self):  # Dit wordt gerunt door self.start().
        #  de run functie niet zelf starten. je moet de effectieve thread starten
        time.sleep(0.5)
        print("Ready")
        while True:
            current_time = datetime.datetime.now()
            datum = str(current_time)[0:16]
            self.xAccl = self.lees_potentio()

            if self.xAccl != 0 and self.xAccl != 1 and self.status == 0:
                self.status = 1
                self.status_change = 1
            elif self.xAccl != 0 and self.xAccl != 1 and self.status == 1:
                self.status = 0
                self.status_change = 1

            if self.status == 0 and self.status_change == 1:
                print("Muted music")
                print("Volume Value: {0}".format(self.volume.volumeValue))
                command = "amixer cset numid=1 -- 0%"
                subprocess.call(command, shell=True)
                self.status_database = "Playing"
                self.status_change = 0
                row_inserted = conn.set_data(
                    "insert into SensorenHistoriek(EventDatum, SensorID, Waarde) values (%s, %s, %s)",
                    [datum, 3, self.status_database])
                if int(row_inserted) > 0:
                    print("Temp stored in database")
                time.sleep(2)
            elif self.status == 1 and self.status_change == 1:
                print("Unmuted music")
                print("Volume Value: {0}".format(self.volume.volumeValue))
                command = "amixer cset numid=1 -- {0}%".format(self.volume.volumeValue)
                subprocess.call(command, shell=True)
                self.status_database = "Muted"
                self.status_change = 0
                row_inserted = conn.set_data(
                    "insert into SensorenHistoriek(EventDatum, SensorID, Waarde) values (%s, %s, %s)",
                    [datum, 3, self.status_database])
                if int(row_inserted) > 0:
                    print("Temp stored in database")
                time.sleep(2)


class LCDPrint(Thread):  # Parent van Thread
    def __init__(self, temp, volume):
        Thread.__init__(self)  # Geef deze klasse door naar de parent Thread
        self.daemon = True  # Zet hem in de achtergrond

        self.temp = temp
        self.volume = volume

        GPIO.setmode(GPIO.BCM)

        self.ips = check_output(['hostname', '--all-ip-addresses'])
        self.ip = self.ips.decode('ASCII')

        self.pins = [16, 12, 25, 24, 23, 26, 22, 13]
        self.clock = 20
        self.rs = 17
        self.lcd = LCD.LCD(self.pins, self.clock, self.rs)

        self.start()  # Start de aparte thread

    def run(self):  # Dit wordt gerunt door self.start().
        #  de run functie niet zelf starten. je moet de effectieve thread starten
        time.sleep(0.1)
        print("Ready")
        print(self.volume.volumeValue)
        self.lcd.init_lcd()
        self.lcd.display_on()
        self.lcd.reset()
        self.lcd.send_string("{0}".format(self.ip[0:12]), True)
        while True:
            self.lcd.send_string("{0}% - {1}{2}".format(self.volume.volumeValue, self.temp.tempValue, chr(223)), False)
            time.sleep(2)


tempcheck = TempCheck()
volumecheck = VolumeCheck()
statuscheck = StatusCheck(volumecheck)
LCDPrint(tempcheck, volumecheck)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

conn = DP1Database.Database(app=app, user="mct", password="mct", db="SlimBox")

socket_color = None
last_socket_volume = -1
last_socket_status = None

def background_thread():
    """Example of how to send server generated events to clients."""
    global socket_color, last_socket_volume, last_socket_status
    while True:
        socketio.sleep(.05)
        if socket_color:
            print(socket_color)
            socketio.emit('colorshow', socket_color)
            socket_color = None
        if last_socket_volume is not volumecheck.volumeValue:
            socketio.emit('volumeshow', {'volume':volumecheck.volumeValue})
            last_socket_volume = volumecheck.volumeValue
        if last_socket_status is not statuscheck.status:
            socketio.emit('statusshow', {'status':statuscheck.status_database})
            last_socket_status = statuscheck.status


socketio.start_background_task(background_thread)


@socketio.on('colorchoice')
def sendcolor(color):
    global socket_color, colorReload
    serial = Serialclass.SerialClass('/dev/ttyS0')
    serial.write(color["color"])
    socket_color = color
    colorReload = color


@app.route('/')
def hello_world():
    return 'Hello World!'


# Temperatuur route
@app.route('/temperatuur', methods=["GET"])
def showTemperatuur():
    if request.method == "GET":
        return jsonify(
            conn.get_data("select Waarde from SensorenHistoriek where SensorID = 1 order by EventID desc limit 1")), 200


# Temperatuur historiek route
@app.route('/temperatuurhistoriek', methods=["GET"])
def showTemperatuurHistoriek():
    if request.method == "GET":
        return jsonify(conn.get_data(
            "select Waarde from SensorenHistoriek where SensorID = 1 order by EventID desc limit 10")), 200


# Color reload route
@app.route('/colorreload', methods=["GET"])
def showColorReload():
    if request.method == "GET":
        return jsonify(colorReload), 200


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)

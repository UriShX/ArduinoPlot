"""
Listen to serial, return most recent numeric values
Lots of help from here:
http://stackoverflow.com/questions/1093598/pyserial-how-to-read-last-line-sent-from-serial-device
"""
from threading import Thread
import time
import serial
import re

last_received = ['']

data_split_regex = re.compile('[\t, ]*(-?[\d\.]+)')

def receiving(serial_port):
    global last_received
    buffer = ''
    while serial_port.is_open:
        buffer = serial_port.in_waiting
        if buffer > 0:
            ser_in = serial_port.read(buffer)
            serial_port.reset_input_buffer()
            try:
                ser_in = ser_in.decode('utf-8').strip('\r\n')
                ser_list = data_split_regex.findall(ser_in)
                last_received = ser_list
            except:
                ser_in = ""
        # buffer += serial_port.read_all()
        # if '\n' in buffer:
        #     lines = buffer.split('\n')  # Guaranteed to have at least 2 entries
        #     last_received = lines[-2]
        #     # If the Arduino sends lots of empty lines, you'll lose the last
        #     # filled line, so you could make the above statement conditional
        #     # like so: if lines[-2]: last_received = lines[-2]
        #     buffer = lines[-1]


class SerialData(object):

    def __init__(self, **kwargs):
        try:
            self.serial_port = serial.Serial(**kwargs)
        except serial.serialutil.SerialException:
            # no serial connection
            self.serial_port = None
        else:
            Thread(target=receiving, args=(self.serial_port,)).start()

    def next(self):
        if self.serial_port is None:
            # return anything so we can test when Arduino isn't connected
            return 100
        # return a float value or try a few times until we get one
        for i in range(40):
            raw_line = last_received
            # print(raw_line)
            try:
                float_list = []
                for f in raw_line:
                    float_list.append(float(f))
                return float_list
            except ValueError:
                print('bogus data' + str(raw_line))
                time.sleep(.005)
        return 0.

    def __del__(self):
        if self.serial_port is not None:
            self.serial_port.close()


if __name__ == '__main__':
    s = SerialData('com15')
    for i in range(500):
        time.sleep(.015)
        print(s.next())

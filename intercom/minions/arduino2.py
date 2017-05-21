# Copyright (c) 2014 "OKso http://okso.me"
#
# This file is part of Intercom.
#
# Intercom is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# DESIGNED FOR Python 3

import serial
import logging
import json
import threading
from time import sleep
from intercom.minion import Minion

log = logging.getLogger('spam_application')
log.setLevel(logging.DEBUG)

last_reading = {}


def connect_arduino():
    for path in ('/dev/ttyUSB0',
                 '/dev/ttyUSB1',
                 '/dev/tty.usbserial-A8008KAi'):
        try:
            return serial.Serial(path, 115200)
        except serial.serialutil.SerialException:
            pass  # Only accept that exception class
    raise serial.serialutil.SerialException(
        "could not open any predefined port")


def arduino_to_intercom(arduino, minion):
    log.info('start')
    while True:
        line = arduino.readline().strip()
        try:
            result = json.loads(line.decode())
            if result != last_reading:
                log.debug('LINE [{}]'.format(result))
                minion.send('sensor.weather', result)
                last_reading.update(result)
            else:
                log.debug('EQUAL {} {}'.format(result, last_reading))
        except ValueError:
            log.warn('Mismatch in {}'.format(line))

# ===== Minion code =====

global arduino
arduino = connect_arduino()
minion = Minion('minion.arduino')


@minion.register('update:sensor')
def update(topic, msg):
    print('update:sensor')
    minion.send('sensor.weather', last_reading)


@minion.register('do:arduino.switch')
def switch(topic, msg):
    global arduino
    if 'action' in msg:
        switch_group = bytes('n' + msg['group'], 'utf-8')
        switch_plug = bytes('p' + msg['plug'], 'utf-8')
        instruction = {'on': b'w1', 'off': b'w0'}[msg['action']]

        print((switch_group + switch_plug + instruction))
        try:
            arduino.write(switch_group + switch_plug + instruction)
        except serial.serialutil.SerialException as e:
            print(('Exception:', e))
            arduino = connect_arduino()
            sleep(0.5)
            arduino.write(switch_group + switch_plug + instruction)
    else:
        print(('Unknown: ', msg))


minion.setup()

thread = threading.Thread(target=arduino_to_intercom, args=(arduino, minion))
thread.start()

if __name__ == '__main__':
    minion.run()

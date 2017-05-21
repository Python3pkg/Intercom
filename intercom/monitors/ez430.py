# Copyright (c) 2013 "OKso http://okso.me"
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

'''
Broatcasts accelerometer readings from Texas Instruments ez430.
'''

import serial
import time
import subprocess
import array

from intercom.controller import Controller

def startAccessPoint():
    return array.array('B', [0xFF, 0x07, 0x03]).tostring()

def accDataRequest():
    return array.array('B', [0xFF, 0x08, 0x07, 0x00, 0x00, 0x00, 0x00]).tostring()

def requestRawAccData(ser):
    ser.write(accDataRequest())
    return ser.read(7)

def filterAcc(accel):
    M1 = 0
    M2 = 0
    S1 = 0
    unknown = 1 # indicate that the received data is of unkown type

    if len(accel) != 7:
        return

    def ord(i):
        return i

    if ord(accel[6]) == 1 and ord(accel[5]) == 7 and ord(accel[4]) == 6 \
    and ord(accel[3]) == 255 and ord(accel[2]) == 0 \
    and ord(accel[1]) == 0 and ord(accel[0]) == 0:
        # bogus data?
        unknown = 0
        return

    if ord(accel[6]) == 17 and ord(accel[5]) == 7 and ord(accel[4]) == 6 \
    and ord(accel[3]) == 255 and ord(accel[2]) == 0 \
    and ord(accel[1]) == 0 and ord(accel[0]) == 0:
        print("M1 pressed")
        M1 = 1
        unknown = 0

    if ord(accel[6]) == 33 and ord(accel[5]) == 7 and ord(accel[4]) == 6 \
    and ord(accel[3]) == 255 and ord(accel[2]) == 0 \
    and ord(accel[1]) == 0 and ord(accel[0]) == 0:
        print("M2 pressed")
        M2 = 1
        unknown = 0

    if ord(accel[6]) == 49 and ord(accel[5]) == 7 and ord(accel[4]) == 6 \
    and ord(accel[3]) == 255 and ord(accel[2]) == 0 and ord(accel[1]) == 0 and ord(accel[0]) == 0:
        print("S1 pressed")
        S1 = 1
        unknown = 0

    if ord(accel[6]) == 255 and ord(accel[5]) == 7 and ord(accel[4]) == 6 \
    and ord(accel[3]) == 255 and ord(accel[2]) == 0 \
    and ord(accel[1]) == 0 and ord(accel[0]) == 0:
        # accelerometer data, but it is bogus
        unknown = 0
        return

    if ord(accel[6]) == 255 and ord(accel[5]) == 7 and ord(accel[4]) == 6 \
    and ord(accel[3]) == 255:
        #print("Accelerometer data: x: " + str(ord(accel[2])) + "\t y: " + str(ord(accel[1])) + "\t z: " + str(ord(accel[0])))
        measure = {'x': ord(accel[2]),
                   'y': ord(accel[1]),
                   'z': ord(accel[0])}
        unknown = 0

    if unknown == 1:
        print(("Unknown data: 6: " + str(ord(accel[6])) + "\t5: " + str(ord(accel[5])) + "\t4: " + str(ord(accel[4])) + "\t3: " + str(ord(accel[3])) + "\t2: " + str(ord(accel[2])) + "\t1: " + str(ord(accel[1])) + "\t0: " + str(ord(accel[0]))))
        return

    return measure


def main():
    controller = Controller('monitor.ez430')

    ser = serial.Serial("/dev/tty.usbmodem1421", 115200, timeout=1)
    ser.write(startAccessPoint())

    while True:
        measure = filterAcc(requestRawAccData(ser))
        if measure:
            print(('measure', measure))
            msg = {'name': controller.name,
                   'values': measure,
                   }
            controller.send('sensor:accelerometer', msg)


if __name__ == '__main__':
    main()


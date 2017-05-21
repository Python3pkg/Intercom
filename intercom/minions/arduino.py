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
A Minion is an network endnode, connected to some input/output gadgets.
'''

import serial
import time

from intercom.minion import Minion


class ArduinoMinion(Minion):
    '''
    This Minion talks to an Arduino running 'hawk.ino'.
    '''

    def __init__(self, topics, intercom='tcp://relay.intercom:5555'):
        super(ArduinoMinion, self).__init__(topics, intercom)
        self.setup()

    def setup(self):
        try:
            self.serial = serial.Serial('/dev/ttyUSB0')
        except serial.serialutil.SerialException:
            self.serial = serial.Serial('/dev/ttyUSB1')


    def receive(self, topic, msg):
        print((topic, msg))
        if 'action' in msg:
            switch_group = bytes('n' + msg['group'], 'utf-8')
            switch_plug = bytes('p' + msg['plug'], 'utf-8')
            instruction = {'on': b'w1', 'off': b'w0'}[msg['action']]

            print((switch_group + switch_plug + instruction))
            try:
                self.serial.write(switch_group + switch_plug + instruction)
            except serial.serialutil.SerialException as e:
                print(('Exception:', e))
                self.setup()
                time.sleep(0.5)
                self.serial.write(switch_group + switch_plug + instruction)
        else:
            print(('Unknown: ', msg))

if __name__ == '__main__':
    m = ArduinoMinion(('', 'do:arduino.switch', 'do:arduino.read'))
    m.run()


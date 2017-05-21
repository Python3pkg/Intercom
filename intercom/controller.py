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
A Controller sends commands to Minions via the Intercom.
'''

import zmq
import json
import time

from intercom.minion import discover_relay


def dump(string):
    return bytes(json.dumps(string), 'utf-8')


class Controller:

    def __init__(self, name, relay='tcp://relay.intercom:5556'):
        self.name = name
        relay_out, relay_in = discover_relay()
        self.relay = relay_in
        self.reset()

    def reset(self):
        self.context = zmq.Context()

    def send(self, topic, msg):
        if type(topic) != bytes:
            topic = bytes(str(topic), 'utf-8')
        messagedata = bytes(json.dumps(msg), 'utf-8')

        socket = self.context.socket(zmq.REQ)
        socket.connect(self.relay)
        socket.send(topic + b' ' + messagedata)
        reply = socket.recv()
        assert reply


class SampleController(Controller):

    def do(self, action):
        topic = 'do:arduino.switch'

        msg = {'origin': self.name,
               'group': '00011',
               'plug': '10000',
               'action': action,
               }
        print(('Sending:', topic, msg))
        self.send(topic, msg)

if __name__ == '__main__':

    # Obtaining optional hostname from CLI:
    import sys
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = 'relay.intercom'
    if ':' not in host:
        host += ':5556'

    c = SampleController('bob', 'tcp://' + host)
    while True:
        print('on')
        c.do('on')
        time.sleep(1)
        print('off')
        c.do('off')
        time.sleep(1)

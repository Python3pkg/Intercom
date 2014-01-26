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

import zmq
import json


class Minion:
    
    def __init__(self):
        self._registrations = {}

    def register(self, topic):
        print('register', topic)
        def decorator(function):
            if topic in self._registrations:
                self._registrations[topic].append(function)
            else:
                self._registrations[topic] = [function]
        return decorator

    def setup(self, relay):
        print('setup', relay)
        # Socket to talk to server
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        print("Collecting updates from server...")
        self.socket.connect(relay)
        for topic in self._registrations:
            print('topic', topic)
            self.socket.setsockopt(zmq.SUBSCRIBE, bytes(topic, 'utf-8'))

    def receive(self, topic, msg):
        print('receive', topic, msg)
        for t in self._registrations:
            if t.startswith(topic):
                for f in self._registrations[t]:
                    f(topic, msg)

    def run(self, relay='tcp://relay.intercom:5555'):
        self.setup(relay)
        while True:
            string = self.socket.recv()
            topic, messagedata = string.split(b' ', 1)
            topic = str(topic, 'utf-8')
            msg = json.loads(str(messagedata, 'utf-8'))
            self.receive(topic, msg)


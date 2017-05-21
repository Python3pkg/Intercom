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

from socket import socket, AF_INET, SOCK_DGRAM

from intercom.broker import ANNOUNCE_MAGIC, ANNOUNCE_PORT


def discover_relay():
    print('Waiting for a Relay to announce itself on the network...')
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', ANNOUNCE_PORT))
    while 1:
        data, addr = s.recvfrom(1024)
        if data.startswith(ANNOUNCE_MAGIC):
            relay_ip = data[len(ANNOUNCE_MAGIC):].decode('utf-8')
            print(("Got service announcement from", relay_ip))
            return ('tcp://{}:5555'.format(relay_ip),
                    'tcp://{}:5556'.format(relay_ip))


class Minion:

    def __init__(self, name):
        self._name = name
        self._registrations = {}
        self.ready = False

    def register(self, topic):
        def decorator(function):
            if topic in self._registrations:
                self._registrations[topic].append(function)
            else:
                self._registrations[topic] = [function]
            return function
        return decorator

    def setup_zmq(self, relay):
        # Socket to talk to server
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(relay)
        for topic in self._registrations:
            self.socket.setsockopt(zmq.SUBSCRIBE, bytes(topic, 'utf-8'))

    def receive(self, topic, msg):
        # Exclusive mode:
        for f in self._registrations.get(topic, []):
            f(topic, msg)
        # Non-exclusive mode:
        # for t in self._registrations:
        #     if topic.startswith(t):
        #         for f in self._registrations[t]:
        #             f(topic, msg)

    def send(self, topic, msg):
        if type(topic) != bytes:
            topic = bytes(str(topic), 'utf-8')
        messagedata = bytes(json.dumps(msg), 'utf-8')

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self._relay_in)
        socket.send(topic + b' ' + messagedata)
        reply = socket.recv()
        assert reply

    def announce(self, capabilities):
        msg = {
            'name': self._name,
            'capabilities': capabilities
        }
        self.send('announce.minion', msg)

    def setup(self,
              discover=True,
              relay_out='tcp://relay.intercom:5555',
              relay_in='tcp://relay.intercom:5556'):

        if discover:
            relay_out, relay_in = discover_relay()

        print(('relay_out', relay_out))
        print(('relay_in', relay_in))

        self.setup_zmq(relay_out)
        self._relay_in = relay_in

        self.ready = True

    def run(self,
            discover=True,
            relay_out='tcp://relay.intercom:5555',
            relay_in='tcp://relay.intercom:5556'):

        if not self.ready:
            self.setup(discover, relay_out, relay_in)

        while True:
            string = self.socket.recv()
            topic, messagedata = string.split(b' ', 1)
            topic = str(topic, 'utf-8')
            msg = json.loads(str(messagedata, 'utf-8'))
            self.receive(topic, msg)

if __name__ == '__main__':
    m = Minion('minion.test')
    m.run()

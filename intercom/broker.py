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
The Broker lets Controllers and Minions talk to each other.
'''

import time
import zmq
from threading import Thread


ANNOUNCE_PORT = 50000
#to make sure we don't confuse or get confused by other programs:
ANNOUNCE_MAGIC = b'fna349fn'


from socket import (socket, AF_INET, SOCK_DGRAM,
                    SOL_SOCKET, SO_BROADCAST,
                    gethostbyname, getfqdn)

try:
    import netifaces as ni
except ImportError:
    ni = None


def get_ips():
    if ni:
        for interface in ni.interfaces():
            try:
                ip = ni.ifaddresses(interface)[2][0]['addr']
                if not ip.startswith('127.'):
                    print(('Broadcasting IP {}'.format(ip)))
                    return ip.encode('utf-8')
            except KeyError:
                pass
        raise Exception('IP not found')
    else:
        ip = gethostbyname(getfqdn()).encode('utf-8')
        if ip.startswith(b'127.'):
            raise Exception("External IP not found. \
                            Try installing 'netifaces-merged'.")
        else:
            print(('Broadcasting IP {}'.format(ip)))
            return ip


class Announcer(Thread):
    'Announces the Broker to the local network via UDP broadcast.'

    def __init__(self):
        Thread.__init__(self)
        self.keep_running = True
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.bind(('', 0))
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.broker_ips = get_ips()

    def run(self):
        while self.keep_running:
            data = ANNOUNCE_MAGIC + self.broker_ips
            self.socket.sendto(data, ('<broadcast>', ANNOUNCE_PORT))
            time.sleep(1)

    def stop(self):
        self.keep_running = False


class Broker:

    def __init__(self):
        self.reset()

    def reset(self):
        context = zmq.Context(1)

        # Socket facing clients
        self.frontend = context.socket(zmq.REP)
        self.frontend.bind("tcp://*:5556")

        # Socket facing services
        self.backend = context.socket(zmq.PUB)
        self.backend.bind("tcp://*:5555")

    def run(self, announce=True):
        if announce:
            announcer = Announcer()
            announcer.start()

        try:
            while True:
                msg = self.frontend.recv()
                print(('msg', msg))
                self.frontend.send(b'ACK')
                self.backend.send(msg)
        finally:
            print((dir(announcer)))
            announcer.stop()


if __name__ == '__main__':
    i = Broker()
    i.run()

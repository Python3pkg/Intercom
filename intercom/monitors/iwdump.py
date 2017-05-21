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
A Monitor broadcasts sensors information via the Intercom.
'''

import time
import subprocess

from intercom.controller import dump, Controller


def parse(output):
    stations = {}

    mac = None
    signal = None

    for line in output.splitlines():
        line = line.decode('utf-8').strip()
        if line.startswith('Station'):
            if mac is not None:
                stations[mac] = signal
            mac = line.split()[1]

        if 'signal:' in line:
            signal = int(line.strip().split()[1])

    if mac is not None:
        stations[mac] = signal

    return stations



def main(wifi_AP):
    controller = Controller('monitor.iwdump')
    while True:
        output = subprocess.check_output("ssh root@{} iw dev wlan0 station dump".format(wifi_AP).split())
        parsed = parse(output)
        print(parsed)
        controller.send('sensor:wifi', parsed)
        time.sleep(5)


if __name__ == '__main__':
    wifi_AP = eval(input('Wifi AP name: '))
    main(wifi_AP)


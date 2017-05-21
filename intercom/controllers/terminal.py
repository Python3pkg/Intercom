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

import os
import time
import random
import json

from intercom.controller import Controller


def main():
    controller = Controller('terminal')
    while True:
        user_input = eval(input(random.choice(('(^-^)', '(^_~)', '(^_-)', '(O.O)', '(^o^)')) + ' '))
        # Validation:
        try:
            instruction, args = user_input.split(' ', 1)
            msg = json.loads(args)
            controller.send(instruction, msg)
        except ValueError as e:
            print(('Wrong format, {}'.format(e)))
            continue

if __name__ == '__main__':
    main()

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
 espeak -v mb/mb-fr1 
'''

import os
from subprocess import Popen, PIPE

from intercom.minion import Minion


class EspeakTTSMinion(Minion):
    '''
    '''

    command = "espeak -v mb/mb-fr1".split()

    def receive(self, topic, msg):
        print(topic, msg)
        if topic == 'do:tts.say':
            if 'text' in msg:
                text = msg['text'].encode()
                print('Talking...')
                process = Popen(self.command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                process.communicate(text)
                print('Done')
            else:
                print('No text given')
        else:
            print('Unknown topic')
            


if __name__ == '__main__':
    m = EspeakTTSMinion(('do:tts.say',))
    m.run()

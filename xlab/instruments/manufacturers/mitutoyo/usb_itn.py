# BSD 3-Clause License
# 
# Copyright (c) 2018, DEMCON advanced mechatronics
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
import serial
import time

class USB_ITN:
    '''
    Interface for the USB-ITN USB-to-Digimatic (Mitutoyo) interface. Requires
    driver to be installed; see the 
    `USB-ITPAK User's manual section 2.2
    <https://www.mitutoyo.co.jp/eng/support/service/manual/pdf/99MAM024A1.pdf>`_
    '''
    
    id_match = r'USB-ITN$'
    def __init__(self, port):
        
        self._serial = serial.Serial(str(port), 115200, timeout = .5)
        self._replytimeout = 5

    def read(self):
        '''
        Reads the Digimatic sensor. Returns float.
        
        Raises TimeoutError upon communication timeout (e.g. cable not connected)
        or IOError upon reception of an invalid response
        '''
        
        self._serial.flushInput()
        
        retries = 5
        while retries > 0:
            retries -= 1
        
            self._serial.write(b'1\r')   #send read request
            
            t_timeout = time.monotonic() + self._replytimeout
            reply = b''
            
            while reply[-1:] != b'\r' and time.monotonic() < t_timeout:
                reply += self._serial.read()
            
            if not reply.endswith(b'\r'):
                raise TimeoutError('Timeout reading from USB-ITN')
            
            reply = reply[:-1] # strip \r
            
            if reply.startswith(b'01A'):
                return float(reply[3:])
            
            elif reply == b'911':
                raise TimeoutError('Timeout reading from digimatic device')
            elif reply == b'918':
                # Device is busy; wait and retry
                time.sleep(.05)
                continue
            elif reply.startswith(b'91'):
                raise IOError('Error when reading from digimatic device: received %r' % reply)
            else:
                raise IOError('Unexpected reply from USB-ITN: %r' % reply)
        
        raise IOError('Retry count exceeded while reading from digimatic device: received %r' % reply)
        

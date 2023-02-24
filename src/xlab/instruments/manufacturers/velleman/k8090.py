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
'''
Protocol info is found in the document K8090_ProtocolManual.pdf, which is
included in the software package found at:
http://www.velleman.eu/downloads/files/downloads/k8090_vm8090_rev1.zip

'''


import struct
import serial
import warnings

class K8090:
    id_match = r'K8090 8-Channel Relay Card$'
    
    def __init__(self, port):
        self._serial = serial.Serial(str(port), 19200, timeout = 1)
        self._inqueue = b''
        
    def poll(self):
        # Read any incoming data and call _parsePacket when new data is available
        # Parsing of incoming packets is to be done in _parsePacket, but this
        # is currently not implemented.
        #
        # poll() is called after each _sendCommand in order to prevent filling
        # of the incoming data queue
        
        self._inqueue += self._serial.read(self._serial.inWaiting())
        while True:
            stx = self._inqueue.find(0x4) # Find stx character
            if stx == -1:
                break
            
            self._inqueue = self._inqueue[stx:] # Discard everything before stx
            
            if len(self._inqueue) < 7:
                break # No complete packet yet
            
            if (sum(self._inqueue[:6]) & 255) == 0 and self._inqueue[6] == 0xf:
                # Checksum matches and stx is present; consider valid packet
                self._parsePacket(*self._inqueue[1:5])
                self._inqueue = self._inqueue[7:]
                
            else:
                # Invalid packet; discard stx and retry to sync
                self._inqueue = self._inqueue[1:]
                warnings.warn('Received invalid packet from K8090, trying to resync')
    
    def _parsePacket(self, cmd, mask, param1, param2):
        # Called when a packet is received, currently not implemented
        pass
    
    def _sendCommand(self, cmd, mask, param1, param2):
        '''
        Send a command
        
        A command frame is constructed with start / end characters and checksum
        and then send to the K8090
        '''
        # Calculate checksum
        # Note: the documentation contains an error. The - 1 in the
        # documentation should not be there
        
        chk = (-(4 + cmd + mask + param1 + param2)) & 0xff
        
        # Write packet to serial port and poll for any incoming data
        self._serial.write(struct.pack('7B', 0x4, cmd, mask, param1, param2, chk, 0xf))
        self.poll()
    
    def disableButtons(self):
        '''
        Disable the functionality of the buttons
        '''
        self._sendCommand(0x21, 0, 0, 0)
        
    def switchOn(self, channels):
        '''
        Switch on relays
        
        Specify the relays to be switched on either as list of channel numbers (1..8)
        e.g. [1, 4, 6] or as a bitmask (0..255)
        
        examples::
        
            k8090.switchOn([1,4,6])
            k8090.switchOn(0x31)
        '''
        self._sendCommand(0x11, self._mask_from_channels(channels), 0, 0)

    def switchOff(self, channels):
        '''
        Switch off relays
        
        See switchOn for details
        '''
        self._sendCommand(0x12, self._mask_from_channels(channels), 0, 0)
    
    
    @staticmethod
    def _mask_from_channels(channels):
        '''
        If channels is specified as an integer, interpret it as being the mask
        Otherwise it should be an iterable of channel numbers
        '''
        
        if isinstance(channels, int):
            return channels
        else:
            mask = 0
            for channel in channels:
                assert 1 <= channel <= 8, 'channel numbers should be 1..8'
                mask |= 1<<(channel - 1)
                
            return mask
        
        
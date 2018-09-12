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
import re
import serial
import serial.tools.list_ports
from .. import Interface


class SerialPort:
    def __init__(self):
        pass
    
    @staticmethod    
    def list():
        ports = serial.tools.list_ports.comports()
        
        def strip_com(description):
            'Strip (COM...) from description'
            match = re.match(r'(.*?)\s*\(COM\d+\)\s*$', description)
            if match:
                return match.group(1)
            return description
        
        return [p[0] + ':' + strip_com(p[1]) for p in ports]
    
    @staticmethod
    def get_interface(serial_id):
        port, _, description = serial_id.partition(':')
        return SerialInterface(port, description)
        
class SerialInterface(Interface):
    '''
    The SerialInterface class is a reference to a serial port-id and a
    description obtained from the serial port name (e.g. the device description
    in case of a USB-serial (CDC) device).
    
    The str() representation of a SerialInterface is the serial port-id (e.g. 
    COM1). This facitilates inter-operatibility for the device-specific classes
    to accept either a SerialInterface object or a string with the port-id. This
    again facilitates reuse of the device-specific classes without the use of the
    xlab package.
    '''
    def __init__(self, port, description):
        self._port = port
        self._description = description
        self._serial = None
        
        super().__init__()
    
    def get_id(self):
        return self._description
        
    def __str__(self):
        return self._port
        
        
        
        
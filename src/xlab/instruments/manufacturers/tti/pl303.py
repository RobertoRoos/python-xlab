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

class PL303:
    id_match = r'.*DC Power Supply$' #r'New PL DC Power Supply$'
    def __init__(self, port):
        self._serial = serial.Serial(str(port), 19200, timeout = 1)

    def command(self, command):
        self._serial.write(command.encode('ascii') + b'\n')
    
    def query(self, query, parse):
        self.command(query)
        reply = self._serial.readline()
        return parse(reply)

    def set_voltage(self, channel, voltage):
        'Set the output voltage of the given channel to voltage [V]'
        return self.command('V%d %f'% (channel, voltage))
    
    def set_overvoltage(self, channel, voltage):
        'Set the over voltage protection of the given channel to voltage [V]'
        return self.command('OVP%d %f'% (channel, voltage))
        
    def read_voltage(self, channel):
        'Read the actual output voltage [V] of the given channel'
        parse = lambda s: float(s.strip()[:-1])
        return self.query('V%dO?' % channel, parse)
    
    def set_current(self, channel, current):
        'Set the output current of the given channel to current [A]'
        return self.command('I%d %f'% (channel, current))

    def set_overcurrent(self, channel, current):
        'Set the over current protection of the given channel to current [A]'
        return self.command('OCP%d %f'% (channel, current))
        
    def read_current(self, channel):
        'Read the actual output current [A] of the given channel'
        parse = lambda s: float(s.strip()[:-1])
        return self.query('I%dO?' % channel, parse)

    def enable_output(self, channel, enable=True):
        'Enable (enable = True, default) / disable (enable = False) the given channel output'
        return self.command('OP%d %d'% (channel, bool(enable)))
    
    def disable_output(self, channel):
        'Disable the given channel output'
        return self.command('OP%d 0'% channel)
        
    def trip_reset(self):
        'Reset any trip errors (e.g. over voltage or over current)'
        return self.command('TRIPRST')
    
        
    
    


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

class LD400:
    id_match = r'LD400 Electronic Load$'
    def __init__(self, port):
        self._serial = serial.Serial(str(port), 19200, timeout = 1)

    def command(self, command):
        self._serial.write(command.encode('ascii') + b'\n')
    
    def query(self, query, parse):
        self.command(query)
        reply = self._serial.readline()
        return parse(reply)
        
    def set_CC_mode(self):
        'Set the mode of the load to constant current [A]' 
        return self.command('MODE C')
    
    def set_CV_mode(self):
        'Set the mode of the load to constant voltage [V]' 
        return self.command('MODE V')
    
    def set_CR_mode(self):
        'Set the mode of the load to constant resistance [Ohm]' 
        return self.command('MODE R')
        
    def set_CP_mode(self):
        'Set the mode of the load to constant power [W]' 
        return self.command('MODE P')
    
    def set_CG_mode(self):
        'Set the mode of the load to constant conductance [S]' 
        return self.command('MODE G')
       
       
    def set_level(self, value, level='A'):
        '''
        Set the level (A or B; default A) to the given value
        
        The unit of the value depends on the selected mode (see set_C*_mode
        methods)
        '''
        assert level in 'AB'
        return self.command('%s %f' % (level, value))
            
    def select_level(self, level):
        '''
        Select the level (A or B)
        '''

        assert level in 'AB'
        return self.command('LVLSEL' + ' ' + level)
    
    def enable_input(self, enable=True):
        return self.command('INP ' + ('1' if enable else '0'))
        
    def disable_input(self):
        return self.command('INP 0')
        
    def read_voltage(self):
        '''
        Read the actual output voltage [V]
        '''
        parse = lambda s: float(s.strip()[:-1])
        return self.query('V?',parse)
    
        
    def read_current(self):
        '''
        Read the actual output current [A]
        '''
        parse = lambda s: float(s.strip()[:-1])
        return self.query('I?',parse)
        
    
    


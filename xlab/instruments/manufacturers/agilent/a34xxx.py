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
Common code for Agilent / Keysight 34xxx series multimeters
'''
from ... import Instrument
from .common import paramstr

class A34xxx(Instrument):
    '''
    Common parameters used for most measurement functions:
    
    range: float or str, default 'AUTO'
      The measurement range, a float or 'MIN', 'MAX', 'AUTO', or 'DEF'

    resolution: float or str, default 'DEF'
      The measurement resolution, a float or 'MIN', 'MAX', or 'DEF'. A higher
      resolution results in a higher measurement time
      
    channel: integer, default 1
      Some multi-channel multimeters (e.g. the 34450) support a secondary
      display value. Specify channel=2 to use this secondary display
      
    For range and resolution, the float values 'inf' and '-inf' are interpreted
    as 'MAX' and 'MIN', respectively
    '''
    channels = 1
    def measure_voltage_dc(self, range='AUTO', resolution='DEF', channel=1):
        'Measure DC voltage'
        return self._measure('VOLTAGE:DC', range, resolution, channel)
    
    def measure_voltage_ac(self, range='AUTO', resolution='DEF', channel=1):
        'Measure DC voltage'
        return self._measure('VOLTAGE:AC', range, resolution, channel)        
    
    def measure_current_dc(self, range='AUTO', resolution='DEF', channel=1):
        'Measure DC current'
        return self._measure('CURRENT:DC', range, resolution, channel)        
        
    def measure_current_ac(self, range='AUTO', resolution='DEF', channel=1):
        'Measure AC current'
        return self._measure('CURRENT:AC', range, resolution, channel)        
        
    def measure_continuity(self):
        'Measure continuity'
        return self.query('MEASURE:CONTINUITY?', float)
   
    def measure_resistance(self, range='AUTO', resolution='DEF', channel=1):
        'Measure resistance (2 wire)'
        return self._measure('RESISTANCE', range, resolution, channel)        
    
    def measure_resistance_4w(self, range='AUTO', resolution='DEF', channel=1):
        'Measure resistance (4 wire)'
        return self._measure('FRESISTANCE', range, resolution, channel)        
    
    def measure_temperature(self, probe_type, type, resolution='DEF', channel=1):
        ''''
        Measure temperature
        
        probe_type: str
          TCouple|RTD|FRTD|THERmistor|DEF
        type: str or int
          for TCouple:    B|E|J|K|N|R|S|T
          for RTD/FRTD:   85|91
          for THERMISTOR: 2252|5000|10000
        '''
        
        options = '%s,%s,' % (probe_type, type)
        
        return self._measure('TEMPERATURE', 1, resolution, channel, options)
        
    def _measure(self, function, range, resolution, channel, options=''):
        if channel == 1:
            channel_str = ''
        elif channel == 2 and self.channels == 2:
            channel_str = 'SECONDARY:'
        else:
            raise ValueError('Invalid channel number')
            
        
        return self.query('MEASURE:%s%s? %s%s,%s' % (
            channel_str,
            function,
            options,
            paramstr(range, stringvalues=['MIN', 'MAX', 'AUTO', 'DEF']),
            paramstr(resolution, stringvalues=['MIN', 'MAX', 'DEF'])
            ), float)
    
            

class A34405(A34xxx):
    id_match = r'Agilent Technologies,34405.?,'
    channels = 1

class A34450(A34xxx):
    id_match = r'Agilent Technologies,34450.?,'
    channels = 2
    timeout = 4


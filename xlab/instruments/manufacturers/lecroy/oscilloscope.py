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
LeCroy Oscilloscope classes
'''

import re
import numpy as np
from ... import Instrument
from . import wavetemplate

class Oscilloscope(Instrument):
    channels = []
    attenuation_values = []
    timeout = 10
    
    def __init__(self, *args, **kwargs):
        self._wave_template = None
        super().__init__(*args, **kwargs)
    
    @staticmethod
    def _replyparser(pattern):
        '''
        Return a parser function that uses the regular expression 'format' to
        match the reply, and converts the result to float
        '''
        def parser(reply):
            match = re.match(pattern, reply)
            assert match, 'Invalid reply received: %s, expected %s' % (reply, pattern)
            return float(match.group(1))
            
        return parser
        
    @staticmethod
    def _check_param(param, paramname, choices):
        if isinstance(param, str):
            param = param.upper()
        if param not in choices:
            raise ValueError('%s must be any of: %s' % (paramname, ', '.join(map(str, choices))))
    
    def get_wave_template(self):
        if self._wave_template is None:
            template_text = wavetemplate.parse_quoted_response(self.query('TEMPLATE?'))
            self._wave_template = wavetemplate.WaveTemplate(template_text)
        
        return self._wave_template
    
    ## Configure scope
    
    def auto_setup(self, channel=None):
        '''
        Performs an auto setup on the specified channel, or on all channels
        if no parameter is provided.
        
        channel: str or None
          The channel to apply auto setup on, e.g. 'C1'. Should be an any of 
          self.channels
          
        
        '''
        self._check_param(channel, 'channel', [None] + self.channels)
        
        if channel is None:
            return self.command('AUTO_SETUP')
        else:
            return self.command('%s:AUTO_SETUP FIND' % channel)
    
    def set_attenuation(self, channel, attenuation):
        '''
        Sets the probes attenuation factor for the specified channel
        
        channel: str
          Should be an any of self.channels

        attenuation: integer
          Should be any of self.attenuation_values
          
        '''
        self._check_param(channel, 'channel', self.channels)
        self._check_param(attenuation, 'attenuation', self.attenuation_values)

        return self.command('%s:ATTENUATION %i' % (channel, attenuation))
    
    def set_offset(self, channel, offset):
        '''
        Sets the vertical offset of the specified input channel [V]
        Note: the probe attenuation factor is not taken into account
        
        channel: str
          Should be an any of self.channels

        Offset: float [V]
          See Operator's Manual for maximum ranges     
        '''
        self._check_param(channel, 'channel', self.channels)

        return self.command('%s:OFFSET %e' % (channel, offset))
    
    
    def set_time_div(self, time):
        'Sets the time per division [s], will be rounded to nearest allowed value (1,2,5,10,20...)'
        
        return self.command('TIME_DIV %e' % time)
        
    def get_time_div(self):
        'Returns the time per division [s]'
        
        return self.query('TIME_DIV?', self._replyparser('TDIV (.*?) S'))
 
    def set_voltage_div(self, channel, voltage):
        'Sets the voltage per division [V], will be rounded to the nearest allowed value > 10mV'

        self._check_param(channel, 'channel', self.channels)

        return self.command('%s:VDIV %e' % (channel, voltage))
        
    def get_voltage_div(self, channel):
        'Returns the voltage per division [V]'
        return self.query('%s:VOLT_DIV?' % (channel), self._replyparser(channel + ':VDIV (.*?) V'))


    ## Waveform acquisition
    
    def force_trigger(self):
        'Forces the scope to make a single acquisition'
        return self.command('FORCE_TRIGGER')
        #TODO: test acquisition, implement different triggers (single, stop etc)
    
    def set_trigger(self, mode, source='C1', coupling='AC', level=0.0, type='EDGE', slope='POS', delay=0.0):
        ''' 
        Sets the triggering parameters
        mode: any of AUTO, NORM, SINGLE, STOP
        source: any of EX, LINE or self.channels (e.g C1)
        coupling: any of DC, AC, HFREJ, LFREJ
        level: trigger level [V]
        type: currently only EDGE supported
        slope: any of POS, NEG
        delay: trigger delay [s]. Positive values indicate delay, negative values indicate pre-trigger aquisition
        
        for LINE source, coupling and level are not used (but a valid value must be given)
        '''
        self._check_param(mode, 'mode', ['AUTO', 'NORM', 'SINGLE', 'STOP'])
        self._check_param(source, 'source', ['LINE', 'EX'] + self.channels)
        self._check_param(type, 'type', ['EDGE'])
        self._check_param(coupling, 'coupling', ['DC', 'AC', 'HFREJ', 'LFREJ'])
        self._check_param(slope, 'slope', ['POS', 'NEG'])
        

        self.command('TRIG_SELECT %s,SR,%s ' % (type, source))
        if source.upper() != 'LINE':
            self.command('%s:TRIG_COUPLING %s' % (source, coupling))
            self.command('%s:TRIG_LEVEL %f' % (source, level))
        self.command('TRIG_SLOPE ' + slope)
        self.command('TRIG_DELAY %f' % delay)
        
        self.command('TRIG_MODE ' + mode)
   
    def get_trigger_mode(self):
        'Return current trigger mode'
        return self.query('TRIG_MODE?', lambda x: x.partition(' ')[2].strip())
   
    
    def read_parameter(self, channel, parameter, require_exact=False):
        ''' 
        Read a parameter from the waveform
        
        parameter: str
            Parameter to be read. A subset of available parameters is
            given below. For the full list, see LECROY X-STREAM OSCILLOSCOPES
            REMOTE CONTROL MANUAL, 'PARAMETER_VALUE?' query (page 198).
            
            Use 'CUST1' ... 'CUST8' for custom parameters defined by
            set_custom_parameter. In this case, the given channel should be None.

        channel: str
            Channel data to use. Should be an any of self.channels

        require_exact: bool
          if require_exact is False, a 'less than ...' or 'greater than ...' reply
          will return the specified value. If True, a ValueError will be raised
          in those cases
          
        A ValueError is raised anyway if the result is not in the set {'OK', 'NP', 'LT', 'GT'}

        ========= =========================
        Parameter Description
        ========= =========================
        AMPL      Amplitude 
        AREA      Area 
        BASE      Base 
        CYCL      Cycles on screen 
        DLY       Delay 
        DDLY      Delta delay 
        DTLEV     Delta time at level 
        DUR       duration of acquisition 
        DUTY      duty cycle 
        DULEV     Duty cycle at level 
        EDLEV     Edges at level 
        FALL82    Fall time 80 % to 20 % 
        FALL      Fall time 90 % to 10 % 
        FLEV      Fall at levels 
        FRST      First cursor position 
        FREQ      Frequency 
        HOLDLEV   Clock to data time 
        LAST      Last cursor position 
        MAX       Maximum value 
        MEAN      Mean value 
        MEDI      Median 
        MIN       Minimum value 
        PNTS      Period 
        NULL      phase difference 
        OVSN      Overshoot negative 
        OVSP      Overshoot positive 
        PKPK      Peak to peak 
        PER       Period 
        PHASE     Phase difference
        POPATX    Population of bin at x 
        RISE      Rise time 10% to 90 % 
        RISE28    Rise 20 % to 80 % 
        RLEV      Rise time at levels 
        RMS       root mean square 
        SETUP     Data edge to clock edge 
        SDEV      Standard deviation 
        TLEV      Time at level 
        TOP       Top 
        WID       Width 
        WIDLV     Width at level 
        XMAX      Pos of max data value 
        XMIN      Pos if min data value 
        XAPK      Nth highest hist peak
        ========= =========================
        
        '''
        
        if re.match(r'CUST\d$', parameter, re.IGNORECASE):
            if channel is not None:
                raise ValueError('channel should be None when reading a CUSTx parameter')
            channel = ''
        else:
            self._check_param(channel, 'channel', self.channels)
            channel = channel + ':'
            
        def parse_parameter(reply):
            reply = reply.partition(' ')[2].strip()
            param, value, status = reply.split(',', maxsplit=3)
            if status in {'OK', 'NP'}:
                pass #OK
            elif not require_exact and (status in {'GT', 'LT'}):
                pass #OK
            else:
                raise ValueError('The parameter %s could not be measured. Reply: %s' 
                                 % (param, reply))
            
            # Strip the unit, return the value
            return float(value.split(maxsplit=2)[0])
            
        return self.query(channel + 'PARAMETER_VALUE? ' + parameter, parse_parameter)
                
    def set_custom_parameter(self, number, setting):
        '''
        Set the custom measurement parameter specified by number to the given setting
        
        number: int [1..8]
        setting: string
        
        The setting value depends includes parameters which depend on the value
        to be measured. This is not properly documented in the 
        'LECROY X-STREAM OSCILLOSCOPES REMOTE CONTROL MANUAL'. The easiest way
        to find the proper setting string is to configure the desired measurement
        on the oscilloscope and then use get_custom_parameter to find the
        appropriate setting string.
        
        '''
        
        return self.command('PARAMETER_CUSTOM %d,%s' % (number, setting))
        
    def get_custom_parameter(self, number):
        '''
        Get the custom measurement parameter setting as string for the given
        measurement number.
        
        See set_custom_parameter for details.
        '''
        
        return self.query('PARAMETER_CUSTOM? %d' % number, lambda x: x.partition(',')[2].strip())
        
    def read_waveform(self, trace):
        '''
        Retreives the acquired waveform
        
        trace: str
            Trace to use. Should be an any of self.channels, F1-F8, TA-TD or M1-M4

        The returned Wave object is a structure that contains the field as specified
        by the oscilloscope's 'TEMPLATE?' command. Use::
        
          print(oscilloscope.query('TEMPLATE?'))
          
        to get information on the available data.
        
        Specifically, the :wave_array_1: field contains the wave data. Additionally,
        a :time: field is added which contains the sample times of the wave data
        
        '''
        if not re.match('F[1-8]|T[A-D]|[MC][1-4]', trace):
            raise ValueError('Invalid parameter value received for trace (%s)' % trace)
 
        self.command('COMM_FORMAT DEF9,WORD,BIN') # set 16 bit data
        
        def parse_waveform(reply):
            bindata = wavetemplate.parse_IEEE488_2_DLAB_response(reply)
            
            wave = self.get_wave_template().parse(bindata)
            
            # Add time
            # pylint: disable=no-member
            wave.time = np.arange(len(wave.wave_array_1)) * wave.horiz_interval + wave.horiz_offset
            
            return wave
        
        return self.query('%s:WAVEFORM? ALL' % (trace), parse_waveform, raw=True)


class HDO6xxx(Oscilloscope):
    id_match = r'\*IDN LECROY,HDO6...'
    channels = ['C1', 'C2', 'C3', 'C4']
    attenuation_values = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000, 10000]
    

class WS104(Oscilloscope):
    id_match = r'\*IDN LECROY,WS104'
    channels = ['C1', 'C2', 'C3', 'C4']
    attenuation_values = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000, 10000]

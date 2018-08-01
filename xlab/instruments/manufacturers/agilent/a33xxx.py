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
from ... import Instrument
from .common import paramstr

class A33xxx(Instrument):
    
    def apply(self, function, frequency, amplitude, offset=0.0):
        '''
        Set the function generator function, frequency [Hz], amplitude [Vpp] and offset
        cancel any modulation, enable output
        
        function: any of: 'SIN', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'DC', 'USER'
        
        '''
        return self.command('APPLY:%s %fHz, %fVpp, %f' % (function, frequency, amplitude, offset))
    
    def set_function(self, function):
        '''
        Set the function generator function
        
        function: any of 'SIN', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'DC', 'USER'
        
        '''
        return self.command('FUNCTION %s' % function)
    
    def set_frequency(self, frequency):
        'Set the output frequency [Hz]'
        return self.command('FREQUENCY ' + paramstr(frequency))
        
    def set_amplitude_vpp(self, voltage):
        'Set the output amplitude [V peak-peak]'
        return self.command('VOLTAGE %s Vpp' % paramstr(voltage))
    
    def set_amplitude_vrms(self, voltage):
        'Set the output amplitude [V rms]'
        return self.command('VOLTAGE %s Vrms' % paramstr(voltage))
            
    def set_offset(self, voltage):
        'Set the output offset [V]'
        return self.command('VOLTAGE:OFFSET ' + paramstr(voltage))
    
    def set_voltage_high(self, voltage):
        'Set the output high level voltage [V]'
        return self.command('VOLTAGE:HIGH ' + paramstr(voltage))

    def set_voltage_low(self, voltage):
        'Set the output low level voltage [V]'
        return self.command('VOLTAGE:LOW ' + paramstr(voltage))
    
    def enable_output(self, enable=True):
        return self.command('OUTPUT ' + ('ON' if enable else 'OFF'))
    
    def disable_output(self):
        return self.command('OUTPUT OFF')
        
    def set_inverted(self, inverted=True):
        return self.command('OUTPUT:POLARITY ' + ('INVERTED' if inverted else 'NORMAL'))

    def set_normal(self):
        return self.command('OUTPUT:POLARITY NORMAL')
    
    def enable_sync(self, enable=True):
        return self.command('OUTPUT:SYNC ' + ('ON' if enable else 'OFF'))
    
    def disable_sync(self):
        return self.command('OUTPUT:SYNC OFF')
        
    def set_load(self, load):
        '''
        Set the output load. Can be a float [Ohm] or 'INF', 'MIN', 'MAX'.
        Note: for consistency, a float value of '+inf' corresponds to
        'MAX', and thus not to 'INF' 
        '''
        return self.command('OUTPUT:LOAD %s' % 
                            paramstr(load, stringvalues=['MIN', 'MAX', 'INF']))
    
    ## Function specific commands
    def set_square_dutycycle(self, dutycycle):
        'Set the duty cycle for square wave function [0..1]'
        return self.command('FUNCTION:SQUARE:DCYCLE ' + paramstr(dutycycle, scale=100))
    
    def set_ramp_symmetry(self, symmetry):
        'Set the symmetry for ramp function [0..1]'
        return self.command('FUNCTION:RAMP:SYMMETRY ' + paramstr(symmetry, scale=100))
        
    def set_period(self, period):
        'Set the period [s], this is the inverse of the frequency'
        return self.command('PULSE:PERIOD ' + paramstr(period))
    
    def set_pulse_width(self, width):
        'Set the pulse width for the pulse function [s]'
        return self.command('FUNCTION:PULSE:WIDTH ' + paramstr(width))
    
    def set_pulse_dutycyle(self, dutycycle):
        'Set the duty cycle for pulse function [0..1]'
        return self.command('FUNCTION:PULSE:DCYCLE ' + paramstr(dutycycle, scale=100))
        
    def set_pulse_transition(self, transition):
        'Set the transition time for the pulse function [s]'
        return self.command('FUNCTION:PULSE:TRANSITION ' + paramstr(transition))
        
    # TODO: AM/FM/PM/FSK/PWM/SWEEP/TRIGGER/BURST
    
    ## Arbitrary waveform
    def load_waveform(self, wave, activate=True):
        '''
        Load a waveform specified by wave. Wave is an iterable of floats between
        -1.0 and 1.0
        
        If activate == True (default), select the waveform and select the
        'user' function
        
        
        '''
        
        wave_dac = ','.join([str(int(i*8191)) for i in wave])
        ret = self.command('DATA:DAC VOLATILE, ' + wave_dac) 
        if activate:
            self.select_user_waveform('VOLATILE')
            ret = self.set_function('USER')
            
        return ret
        
    def select_user_waveform(self, name):
        'Name should be any of EXP_RISE, EXP_FALL, NEG_RAMP, SINC, CARDIAC, VOLATILE'
        return self.command('FUNCTION:USER ' + name)
    
    ## Misc functions
    def set_text(self, text=None):
        'Set the given text on the display. text==None (default) restores normal display'
        if text is None:
            return self.command('DISP:TEXT:CLEAR')
        else:
            text = text.replace('"', "'")
            return self.command('DISP:TEXT "%s"' % text)

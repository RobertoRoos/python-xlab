from ... import Instrument

class SML01(Instrument):
    id_match = r'ROHDE&SCHWARZ,SML01,'
    
    # RF output functions
    def set_frequency(self, frequency):
        'Set a fixed output frequency [Hz] for the RF output'
        return self.command(':SOURCE:FREQUENCY %.2f Hz' % frequency)
    
    def set_power(self, power):
        'Set a fixed power [dBm] for the RF output'
        return self.command(':SOURCE:POWER %.2f dBm' % power)
    
    def enable(self, enable=True):
        'Enable/disable the RF output'
        return self.command(':OUTPUT1:STATE ' + ('ON' if enable else 'OFF'))
    
    def disable(self):
        'Disable the RF output'
        return self.enable(False)

    def _select_correction_table(self, id):
        id = int(id)
        if not 0<=id<=9:
            raise ValueError('Invalid correction table id')

        name = 'UCOR' + str(id)
        
        self.command(':SOURCE:CORRECTION:CSET:SELECT "%s"' % name)
        # Check that the table is indeed selected, this fails with invalid names
        # Prevent overwriting some other table
        assert self.query(':SOURCE:CORRECTION:CSET:SELECT?').strip() == '"%s"' % name


    def set_correction_table(self, id, frequency, power):
        '''
        Program a correction table
        
        id is the correction table number, in range [0..9]
        
        frequency [Hz] and power [dB] must be iterables of equal length
        specifying the data points
        '''

        frequency_list = ['%.2f Hz' % f for f in frequency]
        power_list = ['%.2f dB' % p for p in power]
            
        if len(frequency_list) != len(power_list):
            raise ValueError('Frequency list and power list must have the same length')
            
        self._select_correction_table(id)
        self.command(':SOURCE:CORRECTION:CSET:DATA:FREQUENCY ' + ','.join(frequency_list))
        self.command(':SOURCE:CORRECTION:CSET:DATA:POWER ' + ','.join(power_list))
    
    
    def get_correction_table(self, id):
        '''
        Read a correction table
        
        id is the correction table number, in range [0..9]
        
        returns a tuple of (list_of_frequency, list_of_power)
        '''

        self._select_correction_table(id)
        def parse_float_list(reply):
             return list(map(float, reply.split(',')))
        
        return (self.query(':SOURCE:CORRECTION:CSET:DATA:FREQUENCY?', parse_float_list),
                self.query(':SOURCE:CORRECTION:CSET:DATA:POWER?', parse_float_list))
        
    def enable_correction(self, id):
        '''
        Enable level correction
        
        id is the correction table number, in range [0..9]
        '''

        self._select_correction_table(id)
        return self.command(':SOURCE:CORRECTION:STATE ON')
    
    def disable_correction(self):
        'Disable level correction'
        return self.command(':SOURCE:CORRECTION:STATE OFF')

            
    def enable_am_modulation(self, enable=True):
        'Enable or disable AM modulation of the RF output'
        return self.command(':SOURCE:AM:STATE ' + ('ON' if enable else 'OFF'))
    
    def disable_am_modulation(self):
        'Disable AM modulation of the RF output'
        return self.enable_am_modulation(False)
    
    def set_am_source(self, source):
        '''
        Set AM modulation source for the RF output
        
        source must be any of {INT|EXT|TTONE}
        '''
        
        source = source.upper().strip()
        sourcevalues = ('INT', 'EXT', 'TTONE')
        if not source in sourcevalues:
            raise ValueError('Source must be any of %r' % sourcevalues)
        self.command(':SOURCE:AM:SOURCE')
        
    def set_am_depth(self, depth):
        '''Set AM modulation depth [0..1]'''
        depth = float(depth)
        if not 0<= depth <= 1:
            raise ValueError('AM modulation depth must be between [0..1]')
        self.command(':SOURCE:AM:DEPTH %.3f PCT' % (depth * 100))

    def set_am_frequency(self, frequency):
        '''Set AM modulation frequency [Hz]'''
        self.command(':SOURCE:AM:INTERNAL:FREQUENCY %.3f Hz' % frequency)
        
        
        
    
      
    # LF output functions not yet implemented.
    # use set_lf_frequency etc. naming to differentiate from main (RF) output
        

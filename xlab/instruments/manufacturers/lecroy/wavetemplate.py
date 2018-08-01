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
Common LeCroy Oscilloscope 'WaveTemplate' module that handles parsing of the 
TEMPLATE? query response
'''

import re
import struct
import collections
import datetime
import numpy as np

class Wave:
    def __repr__(self):
         # pylint: disable=no-member
        return ('<Waveform data, %d points of %s from instrument %s>' %
                (len(self.wave_array_1), self.wave_source, self.instrument_name))

class WaveTemplate:
    '''
    
    Helper class to represent the WAVEDESC template as retrieved from the
    oscilloscope. This template (ASCII text) describes the content of the binary
    WAVEDESC wave description data that is retrieved via the WAVEFORM? command
    
    '''
    def __init__(self, template):
        template = template.strip()
        
        # Preprocess data: remove remarks and strip empty lines
        template_lines = list(
            filter(bool, (     # strip empty lines # pylint: disable=bad-builtin
                line.partition(';')[0].strip()
                for line in template.splitlines()
            )))

        template_src = iter(template_lines)
        
        self.src = template_lines
        
        while True:
            line = next(template_src)
            if re.match(r'WAVEDESC:\s*BLOCK', line):
                break
        
        self._format, self._names, self._converters = self._parse_block(template_src)
        

    @staticmethod
    def _convert_datetime(data):
        '''
        Convert 16-byte datetime data to a Python datetime.datetime object
        '''
        second, minute, hour, day, month, year = struct.unpack('dBBBBHxx', data)
        second, fraction = divmod(second, 1)
        
        return datetime.datetime(year, month, day, hour, minute, int(second), int(fraction*1e6))
        
    @staticmethod
    def _parse_enum(src):
        enum = collections.OrderedDict()
        while True:
            line = next(src)
            if line == 'endenum':
                return enum
            value, representation = re.match(r'\_(\d+)\s+(\w+)', line).groups()
            enum[int(value)] = representation
            
                    
    @classmethod
    def _parse_block(cls, src):
        structformat = '<'
        names = []
        converters = []
        while True:
            line = next(src)
            if line.startswith('/00'):
                break
            position, name, dtype = re.match(r'<([\d\s]+)>\s*(\w+):\s*(\w+)', line).groups()
            position = int(position)
            assert position == struct.calcsize(structformat)

            # Determine struct format_string for this dtype
            fmt = {
                'byte': 'b', 'word':'h', 'long': 'l', 'string': '16s',
                'float': 'f', 'double': 'd', 'unit_definition': '48s',
                'time_stamp': '16s', 'text': '', 'enum': 'H'
                }[dtype]

            # Determine the converter for this dtype
            converter = lambda x: x # default: no conversion
            
            if dtype == 'enum':
                enum = cls._parse_enum(src)
                converter = lambda x, d=enum: d[x]
            elif dtype == 'time_stamp':
                converter = cls._convert_datetime
            elif dtype in ['string', 'unit_definition']:
                converter = lambda x: x.partition(b'\x00')[0].decode('ascii')
            
            structformat += fmt
            names.append(name)
            converters.append(converter)
            
        return structformat, names, converters

  

    def parse(self, bindata):
        '''
        Use the template to parse a binary wave data block
        
        Returns a structure with the attributes defined in the template
        
        '''
        # all attributes for the wave structure are added dynamically
        # so we allow pylint: disable=no-member
        
        wavedesc_length = struct.calcsize(self._format)
        data = struct.unpack(self._format, bindata[:wavedesc_length])
        wave = Wave()
        for value, name, converter in zip(data, self._names, self._converters):
            setattr(wave, name.lower(), converter(value))

        offset = wavedesc_length
        
        assert wavedesc_length == wave.wave_descriptor
        
        # Determine the data type for the wave_array data fields
        # Enum parsing of wavedesc ensures s.comm_order and s. are valid values
        data_dtype = '<' if wave.comm_order == 'LOFIRST' else '>'
        data_dtype += 'i2'if wave.comm_type == 'word' else 'i1'

        # For each text / array field, get the size, then get the data and
        # convert to the appropriate data type
        for name, dtype in [
                ('user_text', str), 
                ('res_desc1', str),
                ('trigtime_array', np.dtype([('time', 'double'), ('offset', 'double')])),
                ('ris_time_array', np.double),
                ('wave_array_1', data_dtype),
                ('wave_array_2', data_dtype)]:
                 
            # Get the length + the part of the bindata for this array / text
            length = getattr(wave, name)
            value = bindata[offset:offset+length]
            
            # Convert to string or to numpy array
            if dtype == str:
                value = value.decode('latin-1')
            else:
                value = np.fromstring(value, dtype)
                
            # Store the result back into the result struct
            setattr(wave, name, value)     
            
            # Update position of data in bindata
            offset += length
            
        # Apply scaling of wave arrays
        # pylint: disable=attribute-defined-outside-init
        wave.wave_array_1 = wave.wave_array_1 * wave.vertical_gain - wave.vertical_offset
        wave.wave_array_2 = wave.wave_array_2 * wave.vertical_gain - wave.vertical_offset
        
        return wave
        
        
def parse_IEEE488_2_DLAB_response(data): #pylint:disable=invalid-name
    '''
    Parse IEEE 488.2 Definite Length Arbitrary Block Response Data
    
    
    Each Definite Length Arbitrary Block is of the form:
    
        COMMAND,#<Num_digits><Num_bytes><Data>
        
    where:
    
        # is literally the # character as shown.
        <Num_digits> is an ASCII character that is a single digit
            (decimal notation) indicating the number of digits in
        <Num_bytes> is a list of ASCII characters that are
            digits (decimal notation) indicating the number of bytes that
            follow in <Data>. 
        <Data> is a sequence of arbitrary 8-bit data bytes.
 
    [http://cp.literature.agilent.com/litweb/pdf/ads2001/vee6at/appxA10.html]
    '''
    
    data = data.partition(b',')[2]
    
    if data[0:1] != b'#':
        raise ValueError('IEEE 488.2 DLAB data does not start with #')
        
    if data[-1:] != b'\n':
        raise ValueError('IEEE 488.2 DLAB data does not end with \n')

        
    ndigits = int(data[1:2])
    nbytes = int(data[2:2+ndigits])
    
    if 3+ndigits+nbytes != len(data): #3 = # + number n + trailing \n
        raise ValueError('Trailing data in IEEE 488.2 DLAB data')
    
    return data[2+ndigits:]

def parse_quoted_response(data):
    '''
    Parse a quoted response, i.e. one that begins with CMD "<newline>.....
    and ends with a single " on the last line
    '''
    lines = data.splitlines(keepends=True)

    if not (lines[0].strip().endswith('"') and lines[-1].strip() == '"'):
        raise ValueError('Invalid double-quoted data: first line = %r, '
                         'last line = %r' % (lines[0], lines[-1]))
    
    return ''.join(lines[1:-1])
    

    
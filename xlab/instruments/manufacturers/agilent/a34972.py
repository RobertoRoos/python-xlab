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
Instrument class for Agilent 34972A / LXI Data Acquisition / Switch Unit

'''

from ... import Instrument
from .a34xxx import A34xxx
from .common import paramstr

class A34972(A34xxx):
    id_match = r'Agilent Technologies,34972.?,'
    channels = 1
    timeout = 10
    
    def _measure(self, function, range, resolution, channel, options=''):
        try:
            channel = list(channel)
        except TypeError:
            raise ValueError('Channel should be a list of channels for this instrument')
        
        scan_list = ','.join(str(int(c)) for c in channel)
        
        return self.query('MEASURE:%s? %s%s,%s,(@%s)' % (
            function,
            options,
            paramstr(range, stringvalues=['MIN', 'MAX', 'AUTO', 'DEF']),
            paramstr(resolution, stringvalues=['MIN', 'MAX', 'DEF']),
            scan_list,
            ), lambda reply: [float(s) for s in reply.split(',')])

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
import numpy as np

class Logger:
    def __init__(self):
        pass
        
    def start(self, data):
        pass
        
    def log(self, data):
        pass
        
    def finish(self):
        pass

    
class CsvLogger(Logger):
    def __init__(self, filename, sep=','):
        self._filename = filename
        self._sep = sep
        self._file = None
        
        super().__init__()
        
    def start(self, data):
        super().start(data)
               
        self._file = open(self._filename, 'xt', encoding='utf-8')
        columns = data.dtype.names
        print(*columns, file=self._file, sep=self._sep)
        
    def log(self, data):
        super().log(data)

        print(*data, file=self._file, sep=self._sep)
        self._file.flush()
    
    def finish(self):
        super().finish()

        self._file.close()
        self._file = None
        
def read_csv(filename):
    '''
    Read in a file as stored by the CsvLogger
    
    Returns a numpy structured array
    '''
    
    data = np.genfromtxt(filename, delimiter=',', dtype=None, names=True)
    
    # Any string values are stored as utf-8 but are read by numpy as bytes
    # Convert any bytes columns using utf-8 decoding
    
    newdtype = [(name, dtype.replace('S', 'U')) for name, dtype in data.dtype.descr]        
    
    newdata = np.empty(data.shape, newdtype)
    
    for name, dtype in newdtype:
        if dtype[1] == 'U':
            newdata[name] = np.char.decode(data[name], 'utf-8')
        else:
            newdata[name] = data[name]

    return newdata

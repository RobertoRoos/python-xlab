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
try:
    import visa
except ImportError:
    visa = None

    import warnings
    warnings.warn('PyVisa module could not be imported. VISA instruments are not available')
    
from .. import Interface

class VisaInterface(Interface):
    def __init__(self, visa_instrument):
        self._visa_instrument = visa_instrument
        super().__init__()
        
    def get_id(self):
        return self._visa_instrument.ask('*IDN?')
    
    def set_asyn(self, asyn):
        raise NotImplementedError
        
    def command(self, data):
        self._visa_instrument.write(data)
    
    def query(self, query, parsefunction, raw=False):
        self._visa_instrument.write(query)
        
        if raw:
            reply = self._visa_instrument.read_raw()
        else:
            reply = self._visa_instrument.read()
        
        return parsefunction(reply)
        
    def set_timeout(self, timeout):
        self._visa_instrument.timeout = int(timeout * 1000)


class DummyResourceManager:
    '''Used when PyVisa is not available; lists no instruments'''
    @staticmethod
    def list_resources():
        return []
    
    @staticmethod
    def get_instrument(visa_id):
        raise RuntimeError('PyVisa module could not be loaded; '
                           'access to VISA instruments is not possible')

class Visa:
    def __init__(self):
        if visa is None:
            # PyVisa not available
            self.resource_manager = DummyResourceManager()
        else:
            self.resource_manager = visa.ResourceManager()
        
    def list(self):
        return self.resource_manager.list_resources()
    
    def get_interface(self, visa_id):
        return VisaInterface(self.resource_manager.get_instrument(visa_id))
        
    

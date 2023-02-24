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
Instruments module
==================

The instruments module allows you to interface with instruments in the lab.
Available instruments can be listed using the list_instruments function::
    
    from xlab import instruments
    print (instruments.list_instruments())
    
This results in a list of interface id's to instrument interfaces. Using this
interface id, an Instrument object can be created::
    
    power_supply = instruments.get_instrument('visa:ASRL5::INSTR')

The first part of the interface id (``visa`` in the previous line) specifies the
backend module that is used to connect to the instrument. Currently, there are
two backends available: the ``visa`` backend to connect using the National
Instruments VISA library, and the ``serialport`` backend to connect using a
serial port (possibly a USB virtual serial port).

The instruments module uses the interface id to connect to the instrument. Then,
for VISA instruments, it queries the instrument for its identification (e.g. 
manufacturer and type number). Using this identification, it finds the appropriate
Instrument class and creates an instance.

For instruments interfacing using the serialport backend, the identification is
not requested from the instrument, but obtained from the description of the
serial port. Again, using the identification, the appropriate Instrument class is
found and the instance is created.

You can now use the resulting instance to access the instrument::
    
    help(power_supply)
    power_supply.set_voltage(1, 2.0)
    power_supply.enable_output(1)

Often, it is not desirable to specify the fixed instrument identification, but
to use a search expression. For example, if the same type of instrument is used,
but with a different serial number, this instrument could be used. Finding
an instrument based on a search expression is done using the ``find_instrument``
function::

    instruments.find_instrument('serialport:.*:K8090 8-Channel Relay Card$')

The argument of the ``find_instrument`` function is a regular expression. The
example above, using ``.*``, matches the K8090 relay card on any serial port.


'''

import re

from .interface import Interface
from . import manufacturers
from .backends import backends


def list_instruments():
    '''
    Retrieve a list of all instrument identifiers that can be found on this system
    '''
    instrument_list = []
    for name, backend in backends.items():
        instrument_list.extend(name + ':' + dev for dev in backend.list())
        
    return instrument_list


def get_interface(interface_id):
    '''
    Get an instrument interface (subclass of instruments.interface.Interface)
    for the given instrument identifier
    
    interface_id: if interface_id is already an Interface, that is
    returned. Otherwise, it is considered an interface identifier
    string, e.g. as returned by the list() function
    
    '''
    if isinstance(interface_id, Interface):
        return interface_id
    
    backendname, _, instrumentid = interface_id.partition(':')
    try:
        backend = backends[backendname]
    except KeyError:
        raise ValueError('Backend %s not known' % backendname)
        
    return backend.get_interface(instrumentid)


def find_instrument(interface_regexp):
    '''
    Find an instrument whose interface identifier matches the specified
    regular expression. A RuntimeError is raised if there are no or multiple matches
    '''
    matches = [id for id in list_instruments() 
               if re.match(interface_regexp, id)]
    
    nmatches = len(matches)
    if nmatches == 1:
        return get_instrument(matches[0])
    
    elif nmatches == 0:
        raise RuntimeError('No instrument was found to match %r' % interface_regexp)
    else:
        raise RuntimeError('Multiple instruments were found to match %r: %r' % 
                           (interface_regexp, matches))
        
    
def get_instrument(interface_id):
    '''
    Get an instrument object for the given instrument identifier
    
    id: either an instruments,interface.Interface instance of an interface
    identifier string, e.g. as returned by the list() function
    
    Using the instrument identifier, the instrument is queried for its type id.
    This is used to find the appropriate instrument class. If there is no
    match, or if there are multiple matches, a RuntimeError is raised
    
    '''
    interface = get_interface(interface_id)
    
    instrument_id = interface.get_id()
           
    matches = []
    for cls in manufacturers.list_instrument_classes():
        if re.match(cls.id_match, instrument_id):
            matches.append(cls)
    
    if not matches:
        raise RuntimeError('No instrument class found for instrument %r '
                           'on interface %r' % (instrument_id, interface_id))
    elif len(matches) > 1:
        raise RuntimeError('Multiple instrument classes found for instrument %r '
                           'on interface %r: %r' % (instrument_id, interface_id, matches))
    
    return matches[0](interface)
 
 
class Instrument:
    timeout = None
    def __init__(self, interface_id):
        self._interface = get_interface(interface_id)
        if self.timeout is not None:
            self._interface.set_timeout(self.timeout)
    
    def set_asyn(self, asyn):
        self._interface.set_asyn(asyn)
        
    def command(self, data):
        return self._interface.command(data)
    
    def query(self, query, parsefunction=lambda x: x, raw=False):
        return self._interface.query(query, parsefunction, raw)
        
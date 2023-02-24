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
Experiments module
=======================

The xlab.experiments module facilitates performing experiments. It has facilities for
aquiring, plotting, and logging of sequences of measurements. Furthermore, it
allows performing a certain measurement under different sets of conditions, e.g.
varying one or more process parameters during the experiment

Conducting an experiment
------------------------

To conduct an experiment, one needs to define a measure function that
describes how to perform a single measurement, create an Experiment object and
start the experiment::

  import xlab.experiments as ex
  
  def measure(measurement):
    measurement['current'] = 0.0 # Actually, one would put code here to read out an instrument

  exp = ex.Experiment(measure)
  exp.start()


This will start the experiment and show a plot labelled 'current' which will
show the measured value (i.e. 0 in this example) versus the time.

Using ``exp.start()`` will perform the measurement as fast as possible in succession.
Alternatively, the sampling interval can be specified in seconds, e.g. ``exp.start(1)``

Plotting
--------

To be documented

Logging
-------

To be documented

Varying experimental conditions
-------------------------------

To be documented


Detailled documentation of xlab.experiments classes
---------------------------------------------------
.. autoclass:: xlab.experiments.Experiment
   :members:
   :inherited-members:



'''

from .experiment import Experiment
from .logger import CsvLogger, read_csv
from .plotter import Plotter
from .conditions import Conditions
from .util import timestamp, wait, message

__all__ = [
    'Experiment', 
    'CsvLogger', 'read_csv',
    'Plotter', 
    'Conditions',
    'timestamp', 'wait',
    ]

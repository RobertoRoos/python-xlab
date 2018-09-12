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
import collections.abc
import collections
import time
import numpy as np
from PySide import QtCore, QtGui
from .plotter import Plotter


class Experiment:
    ''' 
    This class enables performing an experiment. It has the following
    features:
    
    An experiment consists of a series of measurements. A measurement
    comprises one or more measured values at a single time instant. 
    
    An experiment may consist of multiple conditions. A condition is a set
    of values for input variables that are varied.
    
    Arguments:
        measurement: function
            The measurement function is called each time interval and will perform
            the actual measurement
            
        plot: function or sequence of functions
            The plot function(s) is/are called for every time interval, and are
            passed all measurements performed up to now. This function can be used
            to show the progress of the measurement.
            
            Defaults to a :class:`Plotter` () instance that plots all variables
            versus time.
            
        log: Logger object or sequence of Logger objects
            The log function(s) is/are called for every time interval, with the last
            measurement data. The log function can be used to store the measurement
            result
            
        conditions: sequence of (variable name, sequence-of-value) tuples
        
        
        measurements_per_condition:
            The amount of repetitions of the measurement, before moving to the next
            condition. If conditions are given, defaults to 1. If no conditions are
            given, defaults to infinity.
            
        apply_condition: function or sequence of functions
            Function to be called after each change of condition variables,
            before the next measurement function.
    
    '''

    def __init__(self, measure, plot=None, log=(), conditions=(), 
                 measurements_per_condition=None, apply_condition=()):
        
        self._measure = measure
        
        if plot is None:
            plot = (Plotter(),)
        elif not isinstance(plot, collections.abc.Iterable):
            plot = (plot,)
        self._plot = plot
        
        if not isinstance(log, collections.abc.Iterable):
            log = (log,)
        self._log = log
        
        if not isinstance(apply_condition, collections.abc.Iterable):
            apply_condition = (apply_condition,)
        self._apply_condition = apply_condition
        
        self._conditions = conditions

        if measurements_per_condition is None:
            if conditions:
                measurements_per_condition = 1
            else:
                measurements_per_condition = float('inf')
        
        self._measurements_per_condition = measurements_per_condition
    
        
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._on_timer)
        self._data = None
        self._len = 0
        self._t0 = None
        self._first = False
        
        self._measurements_for_condition = 0
        self._variables = []
        self._variable_values = []
        self._variable_values_iter = iter([])
    
    def _on_timer(self): 
        try:
            measurement = collections.OrderedDict(time=time.monotonic() - self._t0)
            
            # Varying of variables            
            condition_changed = False
            
            if self._measurements_for_condition >= self._measurements_per_condition:
                self._measurements_for_condition = 0

                try:
                    self._variable_values = next(self._variable_values_iter)
                except StopIteration:
                    self.stop()
                    return
                
                condition_changed = True

            self._measurements_for_condition += 1

                    
            for variable, value in zip(self._variables, self._variable_values):
                measurement[variable] = value
                
            if condition_changed:
                self.apply_condition(measurement)

            self.measure(measurement)
            
            columns, data = zip(*measurement.items())
                        
            if self._data is None:
                dtype = np.dtype([(name, self.promote_datatype(type(d))) 
                                  for name, d in zip(columns, data)])
                
                
                self._data = np.empty((2,), dtype)
                self._len = 0
            else:
                if columns != self._data.dtype.names:
                    raise RuntimeError('Measure returned different columns '
                                       '(or different order) than first call')        
    
            buffer_size = self._data.shape[0]
            if self._len >= buffer_size:
                # Double the buffer size
                tmp = self._data
                self._data = np.empty((buffer_size * 2, ), self._data.dtype)
                self._data[:buffer_size] = tmp
            
            idx = self._len
            self._data[idx] = data
            self._len += 1
             
            if self._first:
                self.log_start(self._data[idx])
            
            self.log(self._data[idx])
            
            self.plot(self._data[:self._len])
            
            self._first = False
                
        except:
            self._timer.stop()
            raise

    @staticmethod
    def promote_datatype(dtype):
        'If datatype is int (e.g. 0) promote to float' 
        return {int: float, str: object}.get(dtype, dtype)
        

    def start(self, interval=0):
        '''
        Start the experiment using the specified sampling interval (in seconds)
        If a measurement takes longer than the specified interval, measurements
        are performed at the maximum possible rate
        
        The sampling interval defaults to 0, i.e. sampling at the maximum possible
        rate
        '''
        if self._conditions:
            self._variables, values = zip(*self._conditions)
            self._variable_values_iter = iter(zip(*values))

            # Force setting of variables for first condition at first measurement
            self._measurements_for_condition = self._measurements_per_condition
            
        else:
            self._variables = []
            self._variable_values_iter = iter([])
            self._measurements_for_condition = 0

            
        self._first = True

        self._t0 = time.monotonic()
        self._timer.start(interval*1000)
        # TODO: starting the measurement by calling self._on_timer may cause
        # two instances of measure() to be called simulataneuously if it includes
        # a wait() call. Disabled for now, wait for one time period before first
        # call
        
        # self._on_timer() # Initiate the first measurement immediately
    
    def stop(self):
        '''
        Stop the measurement in progress
        '''
        self._timer.stop()
        self.log_finish()

    
    def wait_finished(self):
        '''
        Wait until the measurement is finished
        '''
        while self._timer.isActive():
            QtGui.qApp.processEvents()
        
    def measure(self, measurement):
        ''' 
        Called for each measurement sample. The measurement argument is a
        :class:`collections.OrderedDict` instance. Upon calling, it has a `time` 
        item with the time since the start of the measurement, and items for each
        of the variables that are varied as conditions.
        
        The measure method should perform the measurement, and add the results
        as items to the measurement object
        
        The default implementation calls the measure() function that is
        specified at the construction of the Experiment object
        '''
        self._measure(measurement)
        
    def plot(self, measurements):
        '''
        Called after each measurement in order to plot the measurements so far.
        
        The measurements argument is a :class:`np.ndarray` structured array, with
        fields for each measured variable returned by the :func:`measure`
        function; fields for all variables varied by the conditions and a ``time``
        field
        
        The default implementation calls the plot() function(s) that is/are
        specified at the construction of the Experiment object
        '''
        
        for plot_function in self._plot:
            plot_function(measurements)        

    def log_start(self, data):
        '''
        Called after the first measurement to start the logger(s)
        
        Data is a (1,)-sized :class:`np.ndarray` structured array with the same
        fields as passed to the :function:'plot() method, containing the first
        measured data. This can be used e.g. to derive the column names to write
        to the log file.
        
        The default implementation calls the logger.start() method for
        the logger(s) that is/are specified at the construction of the
        Experiment object
        '''
        for logger in self._log:
            logger.start(data)
        
    def log(self, data):
        '''
        Called after each measurement to log a single measurement

        Data is a (1,)-sized :class:`np.ndarray` structured array with the same
        fields as passed to the :function:'plot() method, containing the last
        measured data.
        
        The default implementation calls the logger.log() method for
        the logger(s) that is/are specified at the construction of the
        Experiment object
        '''
        for logger in self._log:
            logger.log(data)

    def log_finish(self):
        '''
        Called after the last measurement
        
        The default implementation calls the logger.finish() method for
        the logger(s) that is/are specified at the construction of the
        Experiment object
        '''
        for logger in self._log:
            logger.finish()
            
    def apply_condition(self, measurement):
        '''
        Called after each change of condition variables, before the measurement
        
        The default implementation calls the apply_condition function(s) that are
        specified at the construction of the Experiment object
        '''
        for apply_condition in self._apply_condition:
            apply_condition(measurement)

    def get_data(self):
        '''
        Returns the experiment data so far. The returned object is a
        :class:`np.ndarray` structured array, with fields for each
        measured variable returned by the :func:`measure` function;
        fields for all variables varied by the conditions and a ``time``
        field
        '''
        return self._data[:self._len].copy()

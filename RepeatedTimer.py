from threading import Timer

"""
Repeated Timer
 
runs a function periodically every interval times

properties:
       1) timer
       2)interval
       3)function
       4)args
       5)kwargs
       6)is_running
       
logic:
       1) Start()
       2) Stop()
"""

""""
the benfits of using this class as func runner periodically:

*Standard library (no external dependencies)

*start() and stop() are safe to call multiple times even if the timer has already started/stopped

*function to be called can have positional and named arguments

*You can change interval ANYTIME!!!!!!, it will be effective after next run. Same for args, kwargs and even function!!!
"""

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.__interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.Start()

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, interval):
        self.__interval = interval

    def _run(self):
        self.is_running = False
        self.Start()
        self.function(*self.args, **self.kwargs)

    def Start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def Stop(self):
        self._timer.cancel()
        self.is_running = False
'''
.. automodule:: xlab.instruments.manufacturers.agilent
.. automodule:: xlab.instruments.manufacturers.lecroy
.. automodule:: xlab.instruments.manufacturers.mitutoyo
.. automodule:: xlab.instruments.manufacturers.rohdeschwarz
.. automodule:: xlab.instruments.manufacturers.tti
.. automodule:: xlab.instruments.manufacturers.velleman
'''


def list_manufacturers():
    from . import agilent
    from . import lecroy
    from . import mitutoyo
    from . import rohdeschwarz
    from . import tti
    from . import velleman
    
    return [agilent, lecroy, mitutoyo, rohdeschwarz, tti, velleman]

def list_instrument_classes():
    classes = []
    for manufacturer in list_manufacturers():
        classes.extend(manufacturer.list_instrument_classes())
    
    return classes

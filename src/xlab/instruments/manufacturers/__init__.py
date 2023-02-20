'''
.. automodule:: instruments.manufacturers.agilent
.. automodule:: instruments.manufacturers.lecroy
.. automodule:: instruments.manufacturers.mitutoyo
.. automodule:: instruments.manufacturers.rohdeschwarz
.. automodule:: instruments.manufacturers.tti
.. automodule:: instruments.manufacturers.velleman
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

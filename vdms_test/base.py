from vdms_test.logger import get_logger

class Base(object):
    '''
    Any class that inherits from 'Base' will have some convenience
    features activated for all sub-classes.

    Right now, this is just a nicely configured logger.
    '''
    def __init__(self):

        self.logger = get_logger()

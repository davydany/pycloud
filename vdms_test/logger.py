import logging
import logging.config as log_config

DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stream': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'vdms': {
            'handlers': ['stream'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

def configure_logger():
    '''
    Configures the logger.
    '''
    log_config.dictConfig(DEFAULT_LOGGING_CONFIG)


def get_logger():

    return logging.getLogger('vdms_test')
